# OpenAI API Key (ensure this is set in env variables or a secure place)
from pydantic import BaseModel, Field
from checkerchain.types.checker_chain import UnreviewedProduct
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from checkerchain.utils.config import OPENAI_API_KEY


class ScoreBreakdown(BaseModel):
    """Detailed breakdown of product review scores."""

    project: int = Field(description="Innovation/Technology score")
    userbase: int = Field(description="Userbase/Adoption score")
    utility: int = Field(description="Utility Value score")
    security: int = Field(description="Security score")
    team: int = Field(description="Team evaluation score")
    tokenomics: int = Field(description="Price/Revenue/Tokenomics score")
    marketing: int = Field(description="Marketing & Social Presence score")
    roadmap: int = Field(description="Roadmap score")
    clarity: int = Field(description="Clarity & Confidence score")
    partnerships: int = Field(
        description="Partnerships (Collabs, VCs, Exchanges) score"
    )


class ReviewScoreSchema(BaseModel):
    """Structured output schema for product reviews."""

    product: str = Field(description="Product name")
    overall_score: int = Field(description="Overall review score out of 100")
    breakdown: ScoreBreakdown = Field(
        description="Breakdown of scores by evaluation criteria"
    )


async def create_llm():
    """
    Create an instance of the LLM with structured output.
    """
    try:
        model = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model="gpt-4o",
            max_tokens=1000,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0,
            stop=["\n\n"],
        )
        return model.with_structured_output(ReviewScoreSchema)
    except Exception as e:
        raise Exception(f"Failed to create LLM: {str(e)}")


async def generate_review_score(product: UnreviewedProduct):
    """
    Generate review scores for a product using OpenAI's GPT.
    """
    prompt = f"""
    You are an expert evaluator analyzing products based on multiple key factors. Review the product below and provide a score out of 100 with a breakdown (0-10 for each criterion). Calculate the overall score as the average of the breakdown scores multiplied by 10.

    **Product Details:**
    - Name: {product.name}
    - Description: {product.description}
    - Category: {product.category}
    - URL: {product.url}
    - Location: {product.location}
    - Network: {product.network}
    - Team: {len(product.teams)} members
    - Marketing & Social Presence: {product.twitterProfile}
    - Current Review Cycle: {product.currentReviewCycle}

    **Evaluation Criteria:**
    1. Project (Innovation/Technology)
    2. Userbase/Adoption
    3. Utility Value
    4. Security
    5. Team
    6. Price/Revenue/Tokenomics
    7. Marketing & Social Presence
    8. Roadmap
    9. Clarity & Confidence
    10. Partnerships

    Scores must be integers between 0 and 10.
    """

    try:
        llm = await create_llm()
        result = await llm.ainvoke(
            [
                SystemMessage(content="You are an expert product reviewer."),
                HumanMessage(content=prompt),
            ]
        )
        return result
    except Exception as e:
        raise Exception(f"Failed to generate review score: {str(e)}")
