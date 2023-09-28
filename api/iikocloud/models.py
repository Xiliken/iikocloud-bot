from decimal import Decimal
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class IdNameModel(BaseModel):
    id: str
    name: str

    def __str__(self):
        return self.name


class BaseResponseModel(BaseModel):
    correlation_id: Optional[str] = Field(alias="correlationId")


class ErrorModel(BaseResponseModel):
    error_description: Optional[str] = Field(alias="errorDescription")
    error: Optional[str]


class CustomErrorModel(ErrorModel):
    status_code: Optional[str]


class OrganizationModel(IdNameModel):
    class ResponseTypeEnum(str, Enum):
        simple = "Simple"
        extended = "Extended"

    class OAddressFormatTypeEnum(str, Enum):
        legacy = "Legacy"
        city = "City"
        international = "International"
        int_no_postcode = "IntNoPostcode"

    country: Optional[str]
    restaurant_address: Optional[str] = Field(alias="restaurantAddress")
    latitude: Optional[Decimal]
    longitude: Optional[Decimal]
    use_uae_addressing_system: Optional[bool] = Field(alias="useUaeAddressingSystem")
    version: Optional[str]
    currency_iso_name: Optional[str] = Field(alias="currencyIsoName")
    currency_minimum_denomination: Optional[Decimal] = Field(alias="currencyMinimumDenomination")
    country_phone_code: Optional[str] = Field(alias="countryPhoneCode")
    marketing_source_required_in_delivery: Optional[bool] = Field(alias="marketingSourceRequiredInDelivery")
    default_delivery_city_id: Optional[str] = Field(alias="defaultDeliveryCityId")
    delivery_city_ids: Optional[List[str]] = Field(alias="deliveryCityIds")
    delivery_service_type: Optional[str] = Field(alias="deliveryServiceType")
    default_call_center_payment_type_id: Optional[str] = Field(alias="defaultCallCenterPaymentTypeId")
    order_item_comment_enabled: Optional[bool] = Field(alias="orderItemCommentEnabled")
    inn: Optional[str]
    addressFormatType: Optional[OAddressFormatTypeEnum] = Field(alias="addressFormatType")
    is_confirmation_enabled: Optional[bool] = Field(alias="isConfirmationEnabled")
    confirm_allowed_interval_in_minutes: Optional[int] = Field(alias="confirmAllowedIntervalInMinutes")
    response_type: ResponseTypeEnum = Field(alias="responseType")

    def __str__(self):
        return self.name


class BaseOrganizationsModel(BaseResponseModel):
    organizations: List[OrganizationModel]

    def __list_id__(self):
        return [org.id for org in self.organizations]
