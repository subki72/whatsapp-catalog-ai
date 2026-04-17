from app.core.config import settings
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from app.models.pydantic_schemas import CatalogItem
from app.core.logger import logger

class AIExtractor:
    def __init__(self):
        self.llm = ChatGroq(
            groq_api_key=settings.GROQ_API_KEY,
            model_name="llama-3.3-70b-versatile",
            temperature=0
        )
        
        self.parser = PydanticOutputParser(pydantic_object=CatalogItem)
        
        self.prompt = PromptTemplate(
            template=(
                "You are an expert data extraction AI. Your task is to extract business catalog "
                "information from the user's unstructured text message.\n\n"
                "User Message:\n"
                "'{user_message}'\n\n"
                "Instructions:\n"
                "Extract the product name, location, menu list, and unique selling points.\n"
                "If any information is missing, use 'Not provided' for strings and an empty array [] for lists.\n\n"
                "{format_instructions}\n"
            ),
            input_variables=["user_message"],
            partial_variables={"format_instructions": self.parser.get_format_instructions()},
        )
        
        self.chain = self.prompt | self.llm | self.parser

    async def extract_catalog_data(self, user_message: str) -> dict:
        """
        Extracts structured catalog data from a given user message.
        """
        try:
            result = await self.chain.ainvoke({"user_message": user_message})
            return result.model_dump()
            
        except Exception as e:
            logger.error(f"Extraction Error: {e}", exc_info=True)
            return {
                "product_name": "Error",
                "location": "Error",
                "menus": [],
                "unique_selling_point": "Failed to extract data"
            }