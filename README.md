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

- `Notebooks/EDA_RuReviews.ipynb`
- `Notebooks/EDA_AOD4.ipynb`

## Ручное пополнение

- `Data/reviews_registry.csv` — реестр отзывов
- `Data/images_registry.csv` — реестр изображений
- `Data/images/` — фотографии

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
