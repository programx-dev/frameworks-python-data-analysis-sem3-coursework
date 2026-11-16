# Python Data Analysis Frameworks — Coursework

Курсовая работа по дисциплине
«Фреймворки Python для анализа данных».

**Семестр:** 3
**Группа:** 201

## Участники

- Смирнов Никита — AOD-4, изображения
- Белехов Егор — RuReviews, тексты

## Исходные датасеты

- RuReviews: https://github.com/sismetanin/rureviews
- AOD-4: https://data.mendeley.com/datasets/cd5z895tr2/1

Для AOD-4 используются только классы Bird и Drone.

## EDA

- `notebooks/EDA_RuReviews.ipynb`
- `notebooks/EDA_AOD4.ipynb`

## Ручное пополнение

- `data/reviews_registry.csv` — реестр отзывов
- `data/annotations/image_sample_ids.json` — реестр общих ID изображений
- `data/images/` — фотографии

## Документы Google Docs

- Журнал учёта работ: ссылка будет добавлена
- Codebook RuReviews: ссылка будет добавлена
- Codebook AOD-4: ссылка будет добавлена

## Разметка отзывов WB / RuReviews

- `data/annotations/review_markup_egor.json` — полный экспорт разметки Егора с общими sample_id: 150 уникальных отзывов, по 50 каждого класса.
- `data/annotations/partner_reviews/review_tasks_partner.json` — те же 150 заданий без ответов и звёзд для независимой разметки Никитой.
- `data/annotations/partner_reviews/README.md` — инструкция импорта и экспорта.
- `data/annotations/partner_reviews/labeling_interface_partner.xml` — интерфейс выбора positive / neutral / negative.
- `data/reviews/` — отдельные исходные JSON тех же заданий. Импортировать либо общий файл, либо отдельные, чтобы не создавать повторы.
- `data/reviews_registry.csv` — реестр принятой партии с происхождением, лицензией и постоянными ID.

Сопоставление разметок выполняется по sample_id. Ответы другого участника до завершения независимой разметки не просматриваются.

## Разметка изображений AOD-4

- `data/images/` — фотографии ручного пополнения, включая подпапку `drones`.
- `data/annotations/image_markup_nikita.json` — разметка Никиты с общими числовыми sample_id.
- `data/annotations/image_sample_ids.json` — постоянное соответствие фотографий и sample_id.
- `data/annotations/partner_images/image_tasks_partner.json` — те же 103 задачи без рамок для независимой разметки Егором.
- `data/annotations/partner_images/README.md` — инструкция запуска, импорта и экспорта на другом компьютере.
- `data/annotations/partner_images/labeling_interface_partner.xml` — интерфейс разметки bird / drone с готовыми сведениями об источниках.

JSON задач импортируется один раз. Дополнительно синхронизировать те же фотографии через Cloud Storage не нужно.
Сопоставление изображений выполняется по data.sample_id. Внутренние ID задач и рамок Label Studio могут различаться.
