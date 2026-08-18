# test_config.py

TEST_DATA = {
    # Основна секція сертифіката
    "telephone": "+380509889999",
    "first_name": "Ivan",
    "last_name": "Petrenko",
    "recipient_first_name": "Simon",
    "recipient_last_name": "Abrams",
    "home_address": "Kiyvska oblast, Petrekivskii rajon, Khutorivka village 03015, 187 Petra Doroshenka str., apt. 87, UA",
    "address_destination": "117 aveniu Volter apt. 67, Avinion, Shampane province.",
    "telephone_destination": "+380974319087",
    "postcode_destination": "33-150",
    "entry_country": "Poland",
    "means_transport": "By car",
    "number_transport": "AO 8245 AI",
    "bip_entry": "Shegini, Rava-Ruska, Yahodyn",

    # Дані тварини №1
    "animal_kind": "Ferret",
    "animal_name": "Avira",
    "sex": "male",  # кому додано
    "chip": "986000000236233",
    "chip_date": "10.07.2024",
    "identification_system": "transponder",
    "chip_location": "withers",
    "birth_date": "04.05.2023",
    "breed": "mestizo",
    "color": "Tabby",
    "vaccine_name": "Rabigen Mono",
    "vaccine_batch": "F9K8",
    "vaccination_date": "15.06.2026",
    "valid_vaccination": "15.06.2027",
    "sample_date": "10.07.2026",
    "name_veterinarian": "Bohdan Kohut",
    "name_treatment": "Drontal",
    "date_treatment": "27.07.2026 13:45",
    "notes_animal": "UA AA 458945",
}

def build_actions(filler):
    """Динамічне створення карти команд для поточного екземпляра filler"""
    return {
        "phone": lambda: filler.fill_telephone(TEST_DATA["telephone"]),
        "owner": lambda: filler.fill_owner_name(TEST_DATA["first_name"], TEST_DATA["last_name"]),
        "recipient": lambda: filler.fill_recipient_name(TEST_DATA["recipient_first_name"], TEST_DATA["recipient_last_name"]),
        "address": lambda: filler.fill_sender_address(TEST_DATA["home_address"]),
        "country": lambda: filler.fill_sender_country("Україна"),
        "region": lambda: filler.fill_origin_region("Львівська"),
        "receipt": lambda: filler.fill_receipt_place(TEST_DATA["address_destination"]),
        "rec_phone": lambda: filler.fill_recipient_phone(TEST_DATA["telephone_destination"], TEST_DATA["telephone"]),
        "zip": lambda: filler.fill_recipient_zipcode(TEST_DATA["postcode_destination"]),
        "transit_country": lambda: filler.fill_first_transit_country(TEST_DATA["entry_country"]),
        "transport_type": lambda: filler.fill_transport_type(TEST_DATA["means_transport"]),
        "transport_num": lambda: filler.fill_transport_number(TEST_DATA["number_transport"]),
        "transit_dash": lambda: filler.fill_transit_country(),
        "border": lambda: filler.fill_border_crossing_point(TEST_DATA["bip_entry"]),
        "add_btn": lambda: filler.click_add_button(),
        "animal_kind": lambda: filler.select_animal_kind(TEST_DATA["animal_kind"]),
        "name": lambda: filler.fill_animal_name(TEST_DATA["animal_name"]),
        "chip": lambda: filler.fill_animal_chip(TEST_DATA["chip"]),
        "sex": lambda: filler.fill_animal_sex(TEST_DATA.get("sex", "Male")),
        "birth": lambda: filler.fill_animal_birth_date(TEST_DATA.get("birth_date")),
        "breed": lambda: filler.fill_animal_breed(TEST_DATA.get("breed")),
        "passport": lambda: filler.fill_animal_passport(TEST_DATA.get("notes_animal")),
        "note": lambda: filler.fill_animal_note(TEST_DATA.get("color")),
        "save_close": lambda: filler.click_save_and_close_button(),
        "next": lambda: filler.click_next_button(),
        "finish": lambda: filler.click_finish_button(),
        "add_proc": lambda: filler.click_add_procedure_button(force=True),
        "vac_date": lambda: filler.fill_action_date(TEST_DATA.get("vaccination_date")),
        "act_type": lambda: filler.select_action_type("Вакцинація"),
        "disease": lambda: filler.select_animal_disease(TEST_DATA.get("disease", "Сказ")),
        "drug": lambda: filler.fill_vet_drug(TEST_DATA.get("vaccine_name")),
        "batch": lambda: filler.fill_batch_number(TEST_DATA.get("vaccine_batch")),
        "valid_from": lambda: filler.fill_valid_from_date(TEST_DATA.get("vaccination_date")),
        "valid_to": lambda: filler.fill_valid_to_date(TEST_DATA.get("valid_vaccination")),
        "sample_date": lambda: filler.fill_blood_sample_date(TEST_DATA.get("sample_date")),
        "save_proc": lambda: filler.click_procedure_save_and_close(),
        "fill_proc": lambda: filler.fill_procedure_card(TEST_DATA),
        "tab_info": lambda: filler.switch_tab("1"),
        "tab_actions": lambda: filler.switch_tab("vetdocumentanimals.animalsactions"),
        "chip_date": lambda: filler.fill_chip_implant_date(TEST_DATA.get("chip_date")),
        "id_sys": lambda: filler.fill_identification_system(TEST_DATA.get("identification_system")),
        "chip_loc": lambda: filler.fill_identity_locality(TEST_DATA.get("chip_location")),
        "issuer": lambda: filler.fill_issuer_institution(TEST_DATA.get("name_veterinarian")),
        "act_treatment": lambda: filler.select_action_type_treatment(),
        "date_treat": lambda: filler.fill_treatment_date(TEST_DATA.get("date_treatment")),
        "disease_echino": lambda: filler.select_disease_echinococcus(),
        "drug_treat": lambda: filler.fill_treatment_drug(TEST_DATA.get("name_treatment")),
        "fill_treat": lambda: filler.fill_treatment_card(TEST_DATA),
        "cert_attrs": lambda: filler.configure_certification_attributes(["433", "434", "435", "438", "441", "443"]),
        
    }





