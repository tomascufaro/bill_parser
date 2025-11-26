from enum import Enum
from typing import Optional
from datetime import date
from pydantic import BaseModel, Field

class DocType(str, Enum):
    INVOICE = "invoice"
    RECEIPT = "receipt"
    CREDIT_NOTE = "credit_note"
    UTILITY_BILL = "utility_bill"
    OTHER = "other"

class Bill(BaseModel):
    doc_type: DocType = Field(..., description="Type of document (invoice, receipt, credit_note)")
    doc_number: str = Field(..., description="Unique identifier of the document")
    issue_date: date = Field(..., description="Date of issuance")
    currency: str = Field(..., description="Currency code (ISO 4217)")
    
    issuer_name: str = Field(..., description="Name of the entity issuing the bill")
    issuer_tax_id: str = Field(..., description="Tax ID of the issuer (VAT/GST/EIN)")
    issuer_address: Optional[str] = Field(None, description="Address of the issuer")
    
    customer_name: Optional[str] = Field(None, description="Name of the recipient")
    customer_tax_id: Optional[str] = Field(None, description="Tax ID of the recipient")
    
    subtotal_amount: float = Field(..., description="Total amount before tax")
    tax_amount: Optional[float] = Field(None, description="Total tax amount")
    total_amount: float = Field(..., description="Final total amount to pay")
    
    description: Optional[str] = Field(None, description="Description of the main item or service")
    quantity: Optional[float] = Field(None, description="Quantity of the main item")
    
    source_filename: Optional[str] = Field(None, description="Name of the processed file")
