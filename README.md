libcloud драйвер для сервиса vscale.io.

## Поддерживаемые методы Compute

### Управление нодами

| Метод              | Поддержка          |
| ------------------ | ------------------ |
| create_node        | #7                 |
| deploy_node        | :heavy_minus_sign: |
| destroy_node       | #8                 |
| features           |                    |
| list_nodes         | :heavy_check_mark: |
| reboot_node        | #17                |
| start_node         | #11                |
| stop_node          | #11                |
| wait_until_running | :heavy_minus_sign: |

### Управление образами

| Метод        | Поддержка          |
| ------------ | ------------------ |
| copy_image   |                    |
| create_image |                    |
| delete_image |                    |
| get_image    |                    |
| list_images  | :heavy_check_mark: |

### Управление дисками

| Метод                   | Поддержка |
| ----------------------- | --------- |
| attach_volume           |           |
| create_volume_snapshot  |           |
| create_volume           |           |
| destroy_volume_snapshot |           |
| destroy_volume          |           |
| detach_volume           |           |
| list_volume_snapshots   |           |
| list_volumes            |           |

### Управление SSH ключами

| Метод                       | Поддержка          |
| --------------------------- | ------------------ |
| create_key_pair             | :heavy_check_mark: |
| delete_key_pair             | :heavy_check_mark: |
| get_key_pair                | :heavy_check_mark: |
| import_key_pair_from_file   | :heavy_minus_sign: |
| import_key_pair_from_string | :heavy_minus_sign: |
| list_key_pairs              | :heavy_check_mark: |

### Остальные

| Метод          | Поддержка          |
| -------------- | ------------------ |
| list_images    | #4                 |
| list_locations | :heavy_check_mark: |
| list_sizes     | #6                 |

## Методы DNS

| Метод                         | Поддержка          | Примечание |
| ----------------------------- | ------------------ | ---------- |
| create record                 | :heavy_check_mark: |            |
| create zone                   | :heavy_check_mark: |            |
| delete record                 | :heavy_check_mark: |            |
| delete zone                   | :heavy_check_mark: |            |
| list records                  | :heavy_check_mark: |            |
| list zones                    | :heavy_check_mark: |            |
| list_record_types             | :heavy_check_mark: | 1          |
| get_record                    | :heavy_check_mark: |            |
| get_zone                      | :heavy_check_mark: |            |
| update record                 | :heavy_check_mark: |            |
| update zone                   | :heavy_check_mark: |            |
| export_zone_to_bind_format    |                    |            |
| export_zone_to_bind_zone_file |                    |            |

1. Поддерживаемые типы получены из документации, в описании метода [`Domains_Records - Создать ресурсную запись для домена.`](https://developers.vds.selectel.ru/documentation/api/v1/#api-Domains_Records-CreateDomainRecord). Возможно поддерживаются и другие типы записей.

# Документация к API

[https://developers.vscale.io/documentation/api/v1/](https://developers.vscale.io/documentation/api/v1/)

## Разработка

В проекте настроена автоматическая проверка линтерами и тестами в GitHub Actions.

### Линтеры

Для запуска линтеров необходимо установить [pre-commit](https://pre-commit.com/). Линтеры запускаются командой `$ pre-commit run -a`.

### Тесты

Тесты запускаются при помощи [pytest](https://pytest.org/).

Для создания фикстур нужен установленный ключ окружения `VSCALE_TOKEN` с API ключём.

### Установка

Github Actions запускаются в `stage: commit`, поэтому в `.pre-commit-config.yaml` проверка `id: no-commit-to-branch` установлена в `stage: push`. Что бы проверка запускалась локально и не срабатывала в CI. Локально надо установить pre-commit хуки на пуши и на коммиты следующей командой:

```bash
$ pre-commit install --hook-type pre-commit --hook-type pre-push
```
