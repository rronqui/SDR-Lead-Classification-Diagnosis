import logging
import uuid

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from src.api.config import settings
from src.graph import NewLeadGraph
from src.models import models
from src.schemas import LeadCreate, LeadResponse
from src.services import hubspot, zapi
from src.services.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/webhooks/zapi", status_code=200)
async def webhook_zapi(raw_request: Request, db: Session = Depends(get_db)):
    body = await raw_request.json()

    if body.get("fromMe", False):
        return {"status": "ignored_outgoing"}

    phone = body.get("phone", body.get("senderPhone", ""))
    phone = phone.strip().lstrip("+")
    message = body.get("message", body.get("text", {}).get("message", ""))

    lead = db.query(models.Lead).filter(models.Lead.numero_whatsapp == phone).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")

    if lead.status not in ["novo", "em_progresso"]:
        return {"status": "ok"}

    interacao = models.InteracaoChatboot(
        lead_id=lead.id,
        tipo="entrada",
        mensagem=message,
        posicao=lead.posicao_pergunta,
    )
    db.add(interacao)
    db.commit()

    if lead.status in ["novo", "em_progresso"]:
        max_perguntas = settings.MAX_PERGUNTAS

        perguntas = db.query(models.PerguntaDiagnostico).filter(
            models.PerguntaDiagnostico.lead_id == lead.id,
            models.PerguntaDiagnostico.validada,
            models.PerguntaDiagnostico.posicao < lead.posicao_pergunta + 1, 
        ).order_by(models.PerguntaDiagnostico.posicao).all()

        historico = []
        for p in perguntas:
            historico.append({
                "pergunta": p.pergunta,
                "resposta": p.resposta or "",
                "objetivo": p.objetivo or "",
                "indicador": p.indicador or "",
            })

        info_empresa = db.query(models.InfoInternetEmpresa).filter(
            models.InfoInternetEmpresa.lead_id == lead.id
        ).first()

        dados_empresa = None
        if info_empresa:
            dados_empresa = {
                "setor_atuacao": info_empresa.setor,
                "score_sdr": info_empresa.dados_json.get("score_sdr"), ## REVISAR AQUI
                "principais_dores_inferidas": info_empresa.descricao or "",
            }

        info_contato = db.query(models.InfoInternetContato).filter(
            models.InfoInternetContato.lead_id == lead.id
        ).first()

        dados_linkedin = None
        if info_contato:
            dados_linkedin = {
                "perfil_linkedin_url": info_contato.linkedin_url,
                "status_validacao": info_contato.status_validacao,
            }

        if lead.posicao_pergunta >= max_perguntas:
            logger.info(f"Lead {lead.id} já completou todas as perguntas")
            return {"status": "completed"}

        pergunta_atual = db.query(models.PerguntaDiagnostico).filter(
            models.PerguntaDiagnostico.lead_id == lead.id,
            models.PerguntaDiagnostico.posicao == lead.posicao_pergunta,
        ).first()

        last_question = (
            pergunta_atual.pergunta
            if pergunta_atual
            else historico[-1]["pergunta"]
            if historico
            else ""
        )

        state = {
            "lead_id": str(lead.id),
            "posicao": lead.posicao_pergunta,
            "max_perguntas": max_perguntas,
            "tentativas": 0,
            "resposta_atual": message,
            "dados_empresa": dados_empresa,
            "dados_linkedin": dados_linkedin,
            "historico": historico,
            "last_question": last_question,
        }

        from src.graph import nodes as graph_nodes
        state = graph_nodes.validar_resposta_node(state)
        validacao_sucesso = state.get("validacao", {}).get("valido", False)

        if not validacao_sucesso:
            feedback = state.get("validacao", {}).get("feedback_usuario", "")
            msg = feedback if feedback else last_question
            zapi.zapi_service.send_message(phone, msg)
            interacao_saida = models.InteracaoChatboot(
                lead_id=lead.id,
                tipo="saida",
                mensagem=msg,
                posicao=lead.posicao_pergunta,
            )
            db.add(interacao_saida)
            db.commit()
            logger.info(f"[DEBUG routes] Sent reenviar message: {msg[:50]}...")
            return {"status": "reenviou"}

        # Buscar a pergunta que foi enviada nesta interação (não filtrar por validada,
        # pois pode ter sido marcada como True na interação anterior)
        pergunta_enviada = db.query(models.PerguntaDiagnostico).filter(
            models.PerguntaDiagnostico.lead_id == lead.id,
            models.PerguntaDiagnostico.posicao == lead.posicao_pergunta,
        ).first()

        if pergunta_enviada:
            last_question = pergunta_enviada.pergunta
        else:
            # Fallback: usar última do histórico
            last_question = historico[-1]["pergunta"] if historico else ""

        existente = db.query(models.PerguntaDiagnostico).filter(
            models.PerguntaDiagnostico.lead_id == lead.id,
            models.PerguntaDiagnostico.posicao == lead.posicao_pergunta,
            models.PerguntaDiagnostico.validada == False,  # noqa: E712
        ).first()

        if existente:
            existente.resposta = message
            existente.validada = True
        else:
            logger.error(
                f"[BUG] Pergunta não encontrada para lead_id={lead.id}, "
                f"posicao={lead.posicao_pergunta}. Isso indica um problema de fluxo."
            )

        historico.append({
            "pergunta": last_question,
            "resposta": message,
            "objetivo": pergunta_enviada.objetivo if pergunta_enviada else "",
            "indicador": pergunta_enviada.indicador if pergunta_enviada else "",
        })

        state["historico"] = historico
        state["resposta_atual"] = ""
        state["posicao"] = lead.posicao_pergunta + 1
        state["validacao"] = {"valido": True}
        state["tentativas"] = 0

        logger.info(f"[DEBUG routes] After validation success - posicao={state['posicao']}, historico_len={len(historico)}, historico={historico}")

        if state["posicao"] >= max_perguntas:
            logger.info(f"[DEBUG routes] Last question answered (posicao={state['posicao']}), calling classificar_lead directly")
            result = graph_nodes.classificar_lead_node(state)
            result = graph_nodes.gerar_diagnostico_node(result)
            result = graph_nodes.gerar_fechamento_node(result)
        else:
            result = graph_nodes.gerar_proxima_pergunta_node(state)
            result["must_continue"] = False

        logger.info(f"[DEBUG routes] After processing - proxima_pergunta={result.get('proxima_pergunta')}, classificacao={result.get('classificacao')}")

        lead.posicao_pergunta += 1

        proxima = result.get("proxima_pergunta", {})
        msg_fechamento = result.get("mensagem_fechamento", "")

        if msg_fechamento:
            zapi.zapi_service.send_message(phone, msg_fechamento)
            interacao_saida = models.InteracaoChatboot(
                lead_id=lead.id,
                tipo="saida",
                mensagem=msg_fechamento,
                posicao=lead.posicao_pergunta,
            )
            db.add(interacao_saida)
            logger.info("[DEBUG routes] Sent fechamento message")
        elif proxima and proxima.get("PERGUNTA"):
            msg = proxima["PERGUNTA"]
            zapi.zapi_service.send_message(phone, msg)
            logger.info(f"[DEBUG routes] Sent proxima pergunta: {msg[:50]}...")

            interacao_saida = models.InteracaoChatboot(
                lead_id=lead.id,
                tipo="saida",
                mensagem=msg,
                posicao=lead.posicao_pergunta,
            )
            db.add(interacao_saida)

            next_pergunta_diag = models.PerguntaDiagnostico(
                lead_id=lead.id,
                posicao=lead.posicao_pergunta,
                pergunta=proxima.get("PERGUNTA", ""),
                objetivo=proxima.get("OBJETIVO", ""),
                indicador=proxima.get("INDICADOR", ""),
                validada=False,
            )
            db.add(next_pergunta_diag)
        else:
            logger.info(f"[DEBUG routes] No message to send - proxima={proxima}, msg_fechamento={msg_fechamento}")

        if lead.posicao_pergunta >= max_perguntas:
            classificacao = result.get("classificacao", {})
            diagnostico = result.get("diagnostico", {})

            if classificacao:
                lead.classificacao = classificacao.get("classificacao")
                lead.score = classificacao.get("score")

            if diagnostico:
                diag_record = models.Diagnostico(
                    lead_id=lead.id,
                    markdown=diagnostico.get("markdown", ""),
                )
                db.add(diag_record)

            info_empresa_data = None
            if info_empresa:
                info_empresa_data = {
                    "faturamento": info_empresa.tamanho or "",
                    "funcionarios": str(info_empresa.tamanho or ""),
                    "setor": info_empresa.setor or "",
                }

            info_contato_data = None
            if info_contato:
                info_contato_data = {
                    "linkedin_url": info_contato.linkedin_url or "",
                }

            hubspot.hubspot_service.update_lead_in_hubspot(
                lead_data={
                    "nome": lead.nome,
                    "email": lead.email or "",
                    "numero_whatsapp": lead.numero_whatsapp,
                    "empresa": lead.empresa,
                    "dominio_empresa": lead.dominio_empresa or "",
                    "cargo": lead.cargo,
                },
                info_empresa=info_empresa_data,
                info_contato=info_contato_data,
                classificacao=classificacao,
            )

            lead.status = "classificado"

        db.commit()

    return {"status": "ok"}


@router.post("/leads", response_model=LeadResponse)
def create_lead(lead_data: LeadCreate, db: Session = Depends(get_db)):
    existing = db.query(models.Lead).filter(
        models.Lead.numero_whatsapp == lead_data.numero_whatsapp
    ).first()

    if existing:
        raise HTTPException(status_code=409, detail="Lead já existe")

    dominio_empresa = lead_data.dominio_empresa
    if not dominio_empresa and lead_data.email and '@' in lead_data.email:
        dominio_empresa = lead_data.email.split('@')[1]

    lead = models.Lead(
        numero_whatsapp=lead_data.numero_whatsapp,
        nome=lead_data.nome,
        email=lead_data.email,
        empresa=lead_data.empresa,
        dominio_empresa=dominio_empresa,
        cargo=lead_data.cargo,
        status="novo",
        posicao_pergunta=0,
    )
    db.add(lead)
    db.commit()
    db.refresh(lead)

    state = {
        "lead_id": str(lead.id),
        "numero_whatsapp": lead.numero_whatsapp,
        "nome": lead.nome,
        "empresa": lead.empresa,
        "dominio": lead.dominio_empresa,
        "cargo": lead.cargo,
    }

    result = NewLeadGraph.invoke(state)

    if result.get("messages"):
        msg = result["messages"][0]["message"]
        zapi.zapi_service.send_message(lead.numero_whatsapp, msg)

        primeira_pergunta = result.get("primeira_pergunta", {}).get("PERGUNTA", "")
        if primeira_pergunta:
            pergunta_diag = models.PerguntaDiagnostico(
                lead_id=lead.id,
                posicao=0,
                pergunta=primeira_pergunta,
                objetivo=result.get("primeira_pergunta", {}).get("OBJETIVO", ""),
                indicador=result.get("primeira_pergunta", {}).get("INDICADOR", ""),
                validada=False,
            )
            db.add(pergunta_diag)

        info_empresa = models.InfoInternetEmpresa(
            lead_id=lead.id,
            razao_social=result.get("dados_empresa", {}).get("razao_social"),
            nome_fantasia=result.get("dados_empresa", {}).get("nome_fantasia"),
            setor=result.get("dados_empresa", {}).get("setor_atuacao"),
            tamanho=result.get("dados_empresa", {}).get("tamanho"),
            descricao=result.get("dados_empresa", {}).get("principais_dores_inferidas"),
            dados_json=result.get("dados_empresa"),
            fonte="serpapi",
        )
        db.add(info_empresa)

        info_contato = models.InfoInternetContato(
            lead_id=lead.id,
            linkedin_url=result.get("dados_linkedin", {}).get("perfil_linkedin_url"),
            cargo_confirmado=result.get("dados_linkedin", {}).get("cargo_confirmado"),
            empresa_confirmada=result.get("dados_linkedin", {}).get("empresa_confirmada"),
            status_validacao=result.get("dados_linkedin", {}).get("status_validacao"),
            dados_json=result.get("dados_linkedin"),
        )
        db.add(info_contato)

        interacao = models.InteracaoChatboot(
            lead_id=lead.id,
            tipo="saida",
            mensagem=msg,
            posicao=0,
        )
        db.add(interacao)

        lead.status = "em_progresso"
        db.commit()

    return lead


@router.get("/leads/{lead_id}", response_model=LeadResponse)
def get_lead(lead_id: uuid.UUID, db: Session = Depends(get_db)):
    lead = db.query(models.Lead).filter(models.Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead não encontrado")
    return lead


@router.get("/leads")
def list_leads(
    status: str = None,
    classificacao: str = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(models.Lead)

    if status:
        query = query.filter(models.Lead.status == status)
    if classificacao:
        query = query.filter(models.Lead.classificacao == classificacao)

    leads = query.offset(skip).limit(limit).all()
    return leads
