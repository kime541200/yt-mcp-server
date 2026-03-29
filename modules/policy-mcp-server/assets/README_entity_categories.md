# Entity Categories Used in Product (PII / PHI)

This document describes the **entity types currently used by the
product** for identifying and redacting sensitive information. The lists
are derived from the original API entity definitions but **filtered to
include only the entities actively used by the product**.

These entities are primarily used in:

-   Named Entity Recognition (NER)
-   Data redaction pipelines
-   Compliance workflows (privacy protection and document sanitization)

------------------------------------------------------------------------

# Overview

  Category                         Count
  -------------------------------- --------
  PII Entities                     **64**
  PHI Entities                     **33**
  Duplicate Entities (PII ∩ PHI)   **5**
  Final Unique Entities            **90**

Duplicate entities appearing in both PII and PHI:

    URL
    CASocialInsuranceNumber
    CABankAccountNumber
    CADriversLicenseNumber
    CAPassportNumber

Total calculation:

    64 + 33 - 5 = 90

------------------------------------------------------------------------

# PII Entity Types (64)

    Person
    Organization
    PersonType
    Address
    Email
    DateTime
    Temperature
    Currency
    Age
    Percentage
    CreditCardNumber
    InternationalBankingAccountNumber
    ABARoutingNumber
    SWIFTCode
    USIndividualTaxpayerIdentification
    USSocialSecurityNumber
    USDriversLicenseNumber
    USUKPassportNumber
    USBankAccountNumber
    ACHRoutingNumber
    InsuranceProvider
    MemberID
    GroupID
    AUDriversLicense
    AUPassportNumber
    AUBusinessNumber
    BSBCode
    UKDriversLicenseNumber
    UKNationalHealthNumber
    UKNationalInsuranceNumber
    Location
    PhoneNumber
    ZipCode
    FaxNumber
    DateOfBirth
    Gender
    SortCode
    VehicleIdentificationNumber
    CustomerReferenceNumber
    TaxFileNumber
    HumanRace
    ReligiousView
    URL
    CATotalIncome150
    CASocialInsuranceNumber
    CABankAccountNumber
    CADriversLicenseNumber
    CAPassportNumber
    Occupation
    PoliticalAffiliation
    SexualPreference
    SocialMediaUrl
    CAPostalCode
    AUPostalCode
    TurkeyPersonalIdentificationNumber
    Appearance
    Country
    Nationality
    CheckNumber
    EmployerIdentificationNumber
    CheckAccountNumber
    NDC

------------------------------------------------------------------------

# PHI Entity Types (33)

    ExaminationName
    Diagnosis
    SymptomOrSign
    TreatmentName
    Allergen
    Course
    MeasurementValue
    Variant
    GeneOrProtein
    MutationType
    Expression
    AdministrativeEvent
    CareEnvironment
    ConditionQualifier
    MedicationName
    Dosage
    FamilyRelation
    BodyStructure
    Direction
    Frequency
    Time
    MeasurementUnit
    RelationalOperator
    HealthcareProfession
    ConditionScale
    MedicationClass
    MedicationForm
    MedicationRoute
    URL
    CASocialInsuranceNumber
    CABankAccountNumber
    CADriversLicenseNumber
    CAPassportNumber

------------------------------------------------------------------------

# Combined Entity List (Unique)

Total: **90 entities**

    Person
    Organization
    PersonType
    Address
    Email
    DateTime
    Temperature
    Currency
    Age
    Percentage
    CreditCardNumber
    InternationalBankingAccountNumber
    ABARoutingNumber
    SWIFTCode
    USIndividualTaxpayerIdentification
    USSocialSecurityNumber
    USDriversLicenseNumber
    USUKPassportNumber
    USBankAccountNumber
    ACHRoutingNumber
    InsuranceProvider
    MemberID
    GroupID
    AUDriversLicense
    AUPassportNumber
    AUBusinessNumber
    BSBCode
    UKDriversLicenseNumber
    UKNationalHealthNumber
    UKNationalInsuranceNumber
    Location
    PhoneNumber
    ZipCode
    FaxNumber
    DateOfBirth
    Gender
    SortCode
    VehicleIdentificationNumber
    CustomerReferenceNumber
    TaxFileNumber
    HumanRace
    ReligiousView
    URL
    CATotalIncome150
    CASocialInsuranceNumber
    CABankAccountNumber
    CADriversLicenseNumber
    CAPassportNumber
    Occupation
    PoliticalAffiliation
    SexualPreference
    SocialMediaUrl
    CAPostalCode
    AUPostalCode
    TurkeyPersonalIdentificationNumber
    Appearance
    Country
    Nationality
    CheckNumber
    EmployerIdentificationNumber
    CheckAccountNumber
    NDC
    ExaminationName
    Diagnosis
    SymptomOrSign
    TreatmentName
    Allergen
    Course
    MeasurementValue
    Variant
    GeneOrProtein
    MutationType
    Expression
    AdministrativeEvent
    CareEnvironment
    ConditionQualifier
    MedicationName
    Dosage
    FamilyRelation
    BodyStructure
    Direction
    Frequency
    Time
    MeasurementUnit
    RelationalOperator
    HealthcareProfession
    ConditionScale
    MedicationClass
    MedicationForm
    MedicationRoute

------------------------------------------------------------------------

# Implementation Example

``` python
SUPPORT_ALL_ENTITY_TYPES = sorted(
    set(SUPPORT_PII_ENTITY_TYPES + SUPPORT_PHI_ENTITY_TYPES)
)
```

------------------------------------------------------------------------

# Notes

-   The API originally supports many more entities, including additional
    country‑specific identifiers.
-   This document reflects the **subset currently enabled in the
    product**.
-   New entities introduced by the API should be reviewed before
    enabling them in production.

------------------------------------------------------------------------

# Recommended Future Improvements

Entities can be grouped into higher-level categories to simplify policy
management:

    IDENTITY
    CONTACT
    FINANCIAL
    DEMOGRAPHIC
    MEDICAL
    GENOMIC
    GENERAL
