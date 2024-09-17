# Databázové systémy - Návrh knižničného systému

## Zmeny oproti predošlému [zadaniu](./library-database-scheme)
Počet bežných tabuliek, prepájacích tabuliek a aj enumov bolo potrebné skresať, keďže endpointy zo zadania nepožadovali až také množstvo detailov, ako môj pôvodný návrh pokrýval. Dôležitou zmenou bolo pridanie `created_at a updated_at` atribútov a `uuid`. Základné vzťahy, ktoré databáza pokrýva sú nasledovné. Mnoho publikácií môže mať mnoho autorov a mnoho kategórií. Publikácia môže mať viacero konkrétnych inštancií, ktoré môžu byť typu `physical, ebook, audiobook` a nadobúdať stav `available, reserved`. Užívateľ môže mať viacej kariet, ktoré môžu nadobúdať status `active, expired, inactive`. Užívateľ môže vytvárať pôžičky `active, returned, overdue` pre danú inštanciu publikácie, tiež môže vytvárať rezervácie pokiaľ nie je žiadna voľná inštancia publikácie. Tabuľky ich atribúty a vzťahy dobre vizualizuje diagram vytvorený pomocou aplikácie DataGrip.

![](https://github.com/FIIT-Databases/dbs23-z5-findura-po14-xslizik/blob/main/documentation/diagram.png)

## Endpointy
Pre toto zadanie som sa rozhodol namiesto čistých sql dopytov využiť ORM, ktoré poskytuje knižnica SQLAlchemy. Táto knižnica umožňuje zadefinovanie prehľadných modelov tabuliek a vzťahov medzi nimi, ktoré zabezpečujú jednoduchú a stabilnú migráciu. API zabezpečuje odpovede na požiadavky typu `GET`, `PATCH`, `POST`, `DELETE`. Kontrola formátov requestov a responses pre jednotlivé endpointy bola vykonaná pomocou schém, knižnice pydantic. Pokiaľ požiadavka nie je v požadovanom formáte je navrátený kód `400`. Pred tým než je vykonaná zmena je vykonaná kontrola, či daný objekt vôbec existuje, ak nie kód `404`, alebo či nedochádza ku konfliktu, kód `409`. Pokiaľ bola požiadavka vykonaná úspešne je navrátený kód úspech `200`, kód vytvorený `201`, alebo kód žiadny obsah `204`.

## USERS

### POST /users
Pred tým než vytvorím užívateľa zistím či dané id náhodou neexistuje a či daný email náhodou neexistuje a následne ho pridám do databázy.
### GET /users/{user_id}
Vyhľadanie usera je vďaka dobre zadefinovaným ORM vzťahov jednoduché stačí ho nájsť a následne dopyt správne sformátovať, aby obsahoval aj objekty rezervácie a pôžičky na ktoré sa odkazuje.

```
SELECT
    users.name,
    users.surname,
    users.email,
    users.birth_date,
    users.personal_identificator,
    users.id,
    users.created_at,
    users.updated_at
FROM users
WHERE users.id = '497f6eca-6276-4993-bfeb-53cbbbba6f08'
LIMIT 1;

SELECT
    rentals.id,
    rentals.user_id,
    rentals.publication_instance_id,
    rentals.duration,
    rentals.start_date,
    rentals.status
FROM rentals
WHERE '497f6eca-6276-4993-bfeb-53cbbbba6f08' = rentals.user_id;

SELECT
    reservations.id,
    reservations.user_id,
    reservations.publication_id,
    reservations.created_at
FROM reservations
WHERE '497f6eca-6276-4993-bfeb-53cbbbba6f08' = reservations.user_id;
```

### PATCH /users/{user_id}
Na to, aby bol user updatenutý musí sa zistiť či existuje, či zadaný mail ešte neexistuje a následne je user zmenený podľa vstupu.

## CARDS

### POST /cards
Pred tým než vytvorím kartu zistím či dané id náhodou neexistuje a či daný užívateľ na ktorého sa viaže existuje a následne ju pridám do databázy.
### GET /cards/{card_id}
Jednoduchý dopyt vyhľadanie karty podľa id.
### PATCH /cards/{card_id}
Pred tým než môže byť karta updatenutá je potrebné zistiť či existuje a či daný poskytnutý užívateľ tiež existuje. Následne sa skontroluje či existujúce id sa naozaj viaže na existujúceho usera a až potom je karta upravená.
### DELETE /cards/{card_id}
Karta je vyhľadaná a vymazaná.

## PUBLICATIONS

### POST /publications
Pred tým než môže byť publikácia vytvorené zisťuje sa či náhodou zadané id už neexistuje, či všetci poskytnutí autori existujú a či všetky poskytnuté kategórie existujú. Publikácia je vytvorená a existujúci
### GET /publications/{publication_id}
Vyhľadaná publikácia na základe id musí byť upravená, aby bola v správnom formáte. Musí obsahovať všetky kategórie aj autorov danej publikácie, ktoré sú naňho naviazané pomocou vzťahov.

```
SELECT
    publications.title,
    publications.id,
    publications.created_at,
    publications.updated_at
FROM publications
WHERE publications.id = %(id_1)s
LIMIT %(param_1)s;

SELECT
    authors.name,
    authors.surname,
    authors.id,
    authors.created_at,
    authors.updated_at
FROM authors, publications_authors
WHERE %(param_1)s = publications_authors.publication_id AND authors.id = publications_authors.author_id;

SELECT
    categories.name,
    categories.id,
    categories.created_at,
    categories.updated_at
FROM categories, publications_categories
WHERE %(param_1)s = publications_categories.publication_id AND categories.id = publications_categories.category_id;
```

### PATCH /publications/{publication_id}
Updatenutie publikácie je veľmi podobné jej vytvoreniu najskôr sa zistí či hľadané id existuje a potom sa zostaví array existujúcich autorov a existujúcich kategórií, ktoré sú priradené relácií, rovnako ako aj všetky nové atribúty.

### DELETE /publications/{publication_id}
Publikácia je vyhľadaná a vymazaná. Po tom ako je zmazaná je v modeloch zadefinované kľúčovým slovom cascade, že sa majú vymazať aj všetky jej inštancie a ich výpožičky a tiež všetky jej rezervácie. Vymazané sú aj záznamy z prepojovacích tabuliek `publications_categories` a `publications_authors`

```
DELETE FROM publications_authors
WHERE publications_authors.publication_id = %(publication_id)s
AND publications_authors.author_id = %(author_id)s;

DELETE FROM publications_categories
WHERE publications_categories.publication_id = %(publication_id)s
AND publications_categories.category_id = %(category_id)s;

DELETE FROM publications
WHERE publications.id = %(id)s;
```

## INSTANCES

### POST /instances
Vytvorenie novej inštancie publikácie prebieha nasledovne. Zistí sa či id už neexistuje, či publikácia na ktorú sa viaže existuje a až následne môže byť vytvorená.
### GET /instances/{instance_id}
Vyhľadanie inštancie na základe id.
### PATCH /instances/{instance_id}
Updatenutie inštancie, skontroluje sa či existuje a či aj publikácia na ktorú sa viaže existuje a jej atribúty sú zmenené.
### DELETE /instances/{instance_id}
Vymazanie inštancie na základe id. Keďže je inštancia naviazaná na pôžičku s kľúčovým slovom cascade ak existuje je spolu s ňou vymazaná.

## AUTHORS

### POST /authors
Vyhľadá sa či dané id ešte neexistuje a či autor s daným menom a priezviskom ešte neexistuje a až následne je Autor vytvorený.
### GET /authors/{author_id}
Vyhľadanie autora na základe id.
### PATCH /authors/{author_id}
Vyhľadá sa či dané id existuje a či meno autora je unikátne.
### DELETE /authors/{author_id}
Vymazanie autora na základe id. Keď je vymazaný sú vymazané aj všetky jeho záznamy z prepojovacej tabuľky `publications_authors`.

## CATEGORIES

### POST /categories
Vyhľadá sa či id ešte neexistuje a či je dané meno unikátne. Kategória je vytvorená.
### GET /categories/{category_id}
Vyhľadanie kategórie na základe id.
### PATCH /categories/{category_id}
Vyhľadá sa či zadané id existuje a či nové meno je unikátne.
### DELETE /categories/{category_id}
Vymazanie kategórie na základe id. Keď je vymazaná sú vymazané aj všetky jej záznamy z prepojovacej tabuľky `publications_authors`

## RENTALS

### POST /rentals
Na to aby mohla byť pôžička vytvorená zisťuje sa či požadované id ešte neexistuje, či užívateľ existuje, či publikácia existuje. Zisťuje sa či existuje dostupná inštancia publikácie zisťuje sa či existujú na danú publikáciu nejaké rezervácie, ak by existovali vyberie sa najstaršia a porovná sa s id zadaného užívateľa, užívateľ si môže publikáciu požičať iba ak je prvý v rade rezervácií. Po vytvorení pôžičky je zmenená hodnota statusu inštancie na `reserved`.
### GET /rentals/{rental_id}
Vyhľadanie pôžičky na základe id.
### PATCH /rentals/{rental_id}
Zisťuje sa či zadané id existuje a atribútu duration je priradená nová hodnota.

## RESERVATIONS

### POST /reservations
Zisťuje sa či zadané id náhodou neexistuje, či užívateľ existuje, či publikácia existuje, či sú všetky jej inštancie nedostupné a až následne môže byť vytvorená rezervácia pre danú publikáciu.
### GET /reservations/{reservation_id}
Vyhľadanie rezervácie na základe id.
### DELETE /reservations/{reservation_id}
Vymazanie publikácie na základe id.
