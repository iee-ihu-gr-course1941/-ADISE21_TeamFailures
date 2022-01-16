# Table of Contents

- [Table of Contents](#table-of-contents)
- [Demo Page](#demo-page)
- [Εγκατάσταση](#εγκατάσταση)
  - [Απαιτήσεις](#απαιτήσεις)
  - [Τεχνολογίες](#τεχνολογίες)
  - [Οδηγίες Εγκατάστασης](#οδηγίες-εγκατάστασης)
    - [Run Backend](#run-backend)
    - [Run Frontend](#run-frontend)
- [Περιγραφή Παιχνιδιού](#περιγραφή-παιχνιδιού)
  - [Συντελεστές](#συντελεστές)
- [Περιγραφή API](#περιγραφή-api)
  - [Methods](#methods)
    - [**Authentication**](#authentication)
    - [**Users**](#users)
    - [**Board**](#board)
- [Περιγραφή βάσης](#περιγραφή-βάσης)
  - [Board](#board-1)
  - [User](#user)

# Demo Page

Μπορείτε να κατεβάσετε τοπικά ή να επισκευτείτε την σελίδα:

https://fastapi-adise21.herokuapp.com/docs#/

# Εγκατάσταση

## Απαιτήσεις

Υπάρχει μέσα στο project o φάκελος requirements για να δείτε τι χρειάζεστε.

## Τεχνολογίες

<img align="left" alt=".Net"  width="50px" src="https://repository-images.githubusercontent.com/260928305/92388600-8d1c-11ea-9993-a726466b5099" /> 
<img align="left" alt="Bootstrap"  width="50px" src="https://miro.medium.com/max/700/0*nkoZ230PgK9FAdkv.png" /> 
<br>

## Οδηγίες Εγκατάστασης

- Κάντε clone το project σε κάποιον φάκελο <br/>
  `$ git clone https://github.com/iee-ihu-gr-course1941/ADISE21_TeamFailures.git `

### Run Backend

- Ανοίξτε τερμάτικο

```
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

- Επισκεφτείτε στην διεύθυνση http://127.0.0.1:8000/docs για να δείτε το API
- https://fastapi-adise21.herokuapp.com/docs#/

### Run Frontend

```
cd frontend
npm i
npm run dev
```

- Επισκεφτείτε στην διεύθυνση http://127.0.0.1:3000 για να δείτε την ιστοσελίδα

# Περιγραφή Παιχνιδιού

- Σε αυτό το παιχνίδι οι παίκτες προσπαθούν να χτίσουν γραμμές από κομμάτια που θα έχουν 1 κοινό χαρακτηριστικό από τα 4 διαφορετικά που υπάρχουν (κάθε κομμάτι έχει 2 από τα 4χαρακτηριστικά). Η δυσκολία όμως έγκειται στο ότι το κομμάτι που θα τοποθετήσουμε κάθε φορά το επιλέγει ο αντίπαλός μας
- Η βάση μας κρατάει τους εξής πίνακες και στοιχεία: Αποθηκεύη χρήστες και Boards, πιο κάτω αναφέρονται πιο αναλύτικα τι περίεχουν οι 2 πίνακες που χρησιμοποιώ.
- Η εφαρμογή απαπτύχθηκε μέχρι το σημείο
  - Backend
    - Authentication
      - Login
      - Create User
    - Users
      - Get User with id
    - Boards
      - Get Boards
      - Create Board
      - Get Random Board
      - Get board with id
      - Update board with id
      - Destroy board with id
  - Frontend
    - Authentication
      - Login
      - Create User
    - Boards
      - Get Random Board
      - Create Board

## Συντελεστές

<!-- Copy-paste in your Readme.md file -->

<a href = "https://github.com/iee-ihu-gr-course1941/ADISE21_TeamFailures/graphs/contributors">
  <img src = "https://contrib.rocks/image?iee-ihu-gr-course1941/ADISE21_TeamFailures = michaeltheo/
ADISE21_TeamFailures"/>
</a>

- Μιχάλης Θεοχάρης: Full Stack

....

# Περιγραφή API

## Methods

### **Authentication**

| Method              | request type | parameters                | Description                                   |
| ------------------- | ------------ | ------------------------- | --------------------------------------------- |
| `api/Auth/login`    | Post         | params: Email,Password    | Επιστρέφει το token για να συνδεθεί ο χρήστης |
| `api/Auth/register` | Post         | body: Email,Password,Name | Κάνει εγγραφή ενός χρήστη                     |

### **Users**

| Method          | request type | parameters | Description                                           |
| --------------- | ------------ | ---------- | ----------------------------------------------------- |
| `api/user/{id}` | Get          | params: id | Επιστρέφει τoν χρήστη ανάλογα με το id που θα δώσουμε |

### **Board**

| Method              | request type | parameters | Description                                      |
| ------------------- | ------------ | ---------- | ------------------------------------------------ |
| `api/boards/`       | Get          |            | Επιστρέφει όλα τα Boards                         |
| `api/boards/random` | Get          |            | Eπιστρέφει ένα board που έχει μόνο 1 παίχτη μέσα |
| `api/boards/{id}`   | Get          | Params: id | Eπιστρέφει το board ανάλογα με το id             |
| `api/boards/`       | Post         |            | Δημιουργεί ένα board                             |
| `api/boards/{id}`   | Put          | Params: id | Ενημερώνει τα στοιχεία ενός συγκεκριμενού board  |
| `api/boards/{id}`   | Delete       | Params: id | Διαγράφη το συγκεκριμένο board                   |

# Περιγραφή βάσης

### Board

Το board είναι ένας πίνακας, ο οποίος στο κάθε στοιχείο έχει τα παρακάτω:

| Attribute       | Description                                                      | TYPE      |
| --------------- | ---------------------------------------------------------------- | --------- |
| `id`            | To id του καθε board                                             | UUID      |
| `creator_id`    | το id του χρήστη που έφτιαξε το board                            | int4      |
| `players`       | Οι παίκτες που είναι μέσα στο board                              | \_varchar |
| `board`         | Το board που είναι μια λίστα με 16 στοιχεία                      | \_varchar |
| `active_player` | O χρήστης που παίζει σε κάθε γύρο                                | varchar   |
| `is Full`       | Ελένχγει αν το board έχει 2 παίχτες ή 1                          | bool      |
| `status`        | Ελένχγει αν το board είναι active δηλαδή αν κάποιος παίζει ή οχι | varchar   |

### User

---

O κάθε παίκτης έχει τα παρακάτω στοιχεία:

| Attribute   | Description                           | TYPE    |
| ----------- | ------------------------------------- | ------- |
| `id`        | To id του χρήστη                      | int4    |
| `name`      | To όνομα του χρήστη                   | varchar |
| `email `    | Το email του χρήστη                   | varchar |
| `password ` | Ο κωδικός του χρήστη κρυπτογραφημένος | varchar |
