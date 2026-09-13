# Retrogram — 2 Instagram поста на ден

Готова автоматизация за публикуване на предварително одобрени изображения в Instagram два пъти дневно. Началната опашка съдържа шест готови поста (три дни).

## Безплатен облак с GitHub Actions

Това е препоръчителният режим. Не е нужен включен компютър, VPS или Cloudinary.

1. Качи проекта в **public** GitHub repository. Public е нужно, за да може Instagram да изтегли изображението.
2. В `Settings → Secrets and variables → Actions` добави два repository secrets:
   - `INSTAGRAM_USER_ID`
   - `INSTAGRAM_ACCESS_TOKEN`
3. В `Settings → Actions → General → Workflow permissions` избери `Read and write permissions`.
4. Отвори `Actions → Instagram - 2 posts daily → Run workflow` и първо избери `preview`.
5. След успешния тест пусни ръчно `publish` за първата публикация. След това графикът работи автоматично.

Графикът е `07:00` и `17:00 UTC`, тоест `10:00` и `20:00` българско лятно време. GitHub може понякога да стартира задачата с кратко закъснение. След успешен пост `data/state.json` се обновява автоматично, за да няма повторения.

## Как работи

1. При стартиране `manifest.json` се зарежда в SQLite опашка.
2. В зададените часове се взема първият непубликуван пост.
3. Изображението временно се качва на публичен HTTPS адрес в Cloudinary.
4. Официалният Instagram API създава и публикува поста.
5. Резултатът се записва; при грешка има до три автоматични опита.

## Нужно преди включване

- Instagram **Professional** профил (Creator или Business).
- Meta Developer приложение с разрешение за публикуване и дългосрочен access token.
- Instagram User ID.
- За локалния режим: Cloudinary и Docker Desktop или Python 3.11+.

## Бърз старт с Docker

1. Копирай `.env.example` като `.env`.
2. Попълни Instagram и Cloudinary стойностите.
3. Остави `DRY_RUN=true` за тест.
4. Стартирай:

```bash
docker compose up -d --build
docker compose logs -f
```

5. Тествай опашката без публикуване:

```bash
docker compose run --rm retrogram python -m retrogram.cli seed
docker compose run --rm retrogram python -m retrogram.cli status
docker compose run --rm retrogram python -m retrogram.cli post-now
```

6. Когато тестът е успешен, смени `DRY_RUN=false` и рестартирай:

```bash
docker compose up -d
```

## Бърз старт без Docker

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
cp .env.example .env
python -m retrogram.cli seed
python -m retrogram.cli post-now
python -m retrogram.worker
```

## Добавяне на нов пост

1. Сложи PNG/JPG изображението в `assets/queue/`.
2. Добави обект с `file` и `caption` в `assets/queue/manifest.json`.
3. Изпълни `python -m retrogram.cli seed` или рестартирай контейнера.

Имената на файловете са уникални: вече зареден файл няма да се дублира.

## Смяна на часовете

В `.env`:

```env
POST_TIME_1=10:00
POST_TIME_2=20:00
TIMEZONE=Europe/Sofia
```

## Важни защити

- `.env` е изключен от Git и не трябва да се изпраща на никого.
- Автоматизацията стартира в `DRY_RUN=true` и няма да публикува преди изрично да го смениш.
- Използва се официалният API; не се съхранява Instagram парола.
- Провери първите публикации ръчно, преди да оставиш процеса без надзор.

Виж `CONTENT_BIBLE.md` за постоянния стил, био и 30 следващи сцени.
