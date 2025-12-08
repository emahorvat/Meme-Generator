# Meme Generator

Meme Generator je dockerizirana spletna aplikacija za vnašanje smešnega besedila na fotografije, tj. ustvarjanja meme-ov.

## Funkcionalnosti aplikacije

Aplikacija omogoča:
- nalaganje fotografij preko spletnega HTML vmesnika
- vnašanje spodnjega in/ali zgornjega besedila na fotografijo (standarden meme format)
- avtomatsko generiranje meme-a s klikom na gumb
- prenos novo ustvarjenega meme-a v PNG formatu

## Uporabljene tehnologije

#### Backend
- Python 3.12 - programski jezik
- Flask 3.0.0 - web framework
- Pillow 10.1.0 - obdelava fotografij

#### Frontend
- HTML5
- CSS3
- JavaScript

## Navodila za zagon v Dockerju

#### 1. Zgradite image
```bash
docker build -t meme-generator .
```

#### 2. Zaženite container
```bash
docker run -p 5000:5000 meme-generator
```

#### 3. Odprite brskalnik
```
http://localhost:5000
```
