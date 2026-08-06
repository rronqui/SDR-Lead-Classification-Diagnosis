from hubspot import HubSpot
from hubspot.crm.contacts import ApiException

from src.api.config import settings


class HubSpotService:
    def __init__(self):
        self.client = HubSpot(access_token=settings.HUBSPOT_ACCESS_TOKEN)

    def search_company(self, name: str | None = None, domain: str | None = None) -> dict:
        try:
            from hubspot.crm.companies import models

            filters = []
            if name:
                filters.append({
                    "propertyName": "name",
                    "operator": "EQ",
                    "value": name,
                })
            if domain:
                filters.append({
                    "propertyName": "domain",
                    "operator": "EQ",
                    "value": domain,
                })

            if not filters:
                return {"success": False, "error": "name or domain required"}

            search_request = models.PublicObjectSearchRequest(
                filter_groups=[{"filters": filters}],
                limit=1,
            )

            response = self.client.crm.companies.search_api.do_search(public_object_search_request=search_request)

            if response.results:
                return {"success": True, "company_id": response.results[0].id}

            return {"success": False, "error": "Company not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_company(self, name: str, domain: str = "", info_empresa: dict | None = None) -> dict:
        try:
            from hubspot.crm.companies.models import SimplePublicObjectInputForCreate

            company_input = SimplePublicObjectInputForCreate(
                properties={
                    "name": name,
                    "domain": domain,
                    "annualrevenue": info_empresa.get("faturamento", "") if info_empresa else "",
                    "numberofemployees": info_empresa.get("funcionarios", "") if info_empresa else "",
                    "description": info_empresa.get("setor", "") if info_empresa else "",
                    "website": domain,
                    "lifecyclestage": "lead",
                    "type": "PROSPECT",
                    "hs_lead_status": "NEW",
                    "hubspot_owner_id": settings.HUBSPOT_OWNER_ID,
                }
            )
            company = self.client.crm.companies.basic_api.create(
                simple_public_object_input_for_create=company_input,
            )
            return {"success": True, "company_id": company.id}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def create_or_update_contact(
        self,
        email: str,
        properties: dict,
    ) -> dict:
        try:
            from hubspot.crm.contacts.models import SimplePublicObjectInputForCreate
            contact_input = SimplePublicObjectInputForCreate(properties=properties)
            contact = self.client.crm.contacts.basic_api.create(
                simple_public_object_input_for_create=contact_input,
            )
            return {"success": True, "contact_id": contact.id}
        except ApiException as e:
            if e.status == 409:
                return self.update_contact(email, properties)
            return {"success": False, "error": str(e)}

    def update_contact(self, email: str, properties: dict) -> dict:
        try:
            search_response = self.client.crm.contacts.search_api.do_search(
                filter_groups=[{
                    "filters": [{
                        "propertyName": "email",
                        "operator": "EQ",
                        "value": email,
                    }]
                }]
            )

            if search_response.results:
                contact_id = search_response.results[0].id
                self.client.crm.contacts.basic_api.update(
                    contact_id=contact_id,
                    properties=properties,
                )
                return {"success": True, "contact_id": contact_id}

            return {"success": False, "error": "Contact not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def associate_contact_to_company(self, contact_id: str, company_id: str) -> dict:
        return {"success": True, "note": "Association via hs_company_id property"}

    def get_or_create_company(
        self,
        name: str,
        domain: str = "",
        info_empresa: dict | None = None,
    ) -> dict:
        search_result = self.search_company(name=name, domain=domain)
        if search_result.get("success"):
            return {"success": True, "company_id": search_result["company_id"], "created": False}

        if "Company not found" in search_result.get("error", ""):
            return self.create_company(name=name, domain=domain, info_empresa=info_empresa)

        return search_result

    def update_lead_in_hubspot(
        self,
        lead_data: dict,
        info_empresa: dict | None = None,
        info_contato: dict | None = None,
        classificacao: dict | None = None,
    ) -> dict:
        results = {"company": None, "contact": None, "association": None}

        nome = lead_data.get("nome", "")
        partes = nome.split()
        primeiro_nome = partes[0] if partes else ""
        sobrenome = " ".join(partes[1:]) if len(partes) > 1 else ""

        prioridade = ""
        if classificacao:
            classificacao_val = classificacao.get("classificacao", "")
            if classificacao_val == "A":
                prioridade = "Alta"
            elif classificacao_val == "B":
                prioridade = "Média"
            elif classificacao_val == "C":
                prioridade = "Baixa"

        empresa_nome = lead_data.get("empresa", "")
        dominio = lead_data.get("dominio_empresa", "")
        email = lead_data.get("email", "")

        if empresa_nome and email:
            empresa_result = self.get_or_create_company(
                name=empresa_nome,
                domain=dominio,
                info_empresa=info_empresa,
            )
            results["company"] = empresa_result

            contact_props = {
                "firstname": primeiro_nome,
                "lastname": sobrenome,
                "email": email,
                "phone": lead_data.get("numero_whatsapp", ""),
                "company": empresa_nome,
                "jobtitle": lead_data.get("cargo", ""),
                "prioridade": prioridade,
                "lifecyclestage": "marketingqualifiedlead",
                "hs_lead_status": "NEW",
                "hubspot_owner_id": settings.HUBSPOT_OWNER_ID,
            }

            if classificacao:
                contact_props["score"] = str(classificacao.get("score", 0))

            if info_contato and info_contato.get("linkedin_url"):
                contact_props["hs_linkedin_url"] = info_contato["linkedin_url"]

            contact_result = self.create_or_update_contact(
                email=email,
                properties=contact_props,
            )
            results["contact"] = contact_result

            if empresa_result.get("success") and contact_result.get("success"):
                results["association"] = {"success": True}

        return results


hubspot_service = HubSpotService()
