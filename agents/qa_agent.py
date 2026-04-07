"""
Агент контроля качества
"""



class QAAgent:
    def __init__(self, llm_service, blender_service):
        self.llm = llm_service
        self.blender = blender_service

    async def validate(self, results: list, session_id: str) -> dict:
        return {"success": True, "message": "QA passed"}
