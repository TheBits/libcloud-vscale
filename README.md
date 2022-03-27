libcloud драйвер для сервиса vscale.io.

## Поддерживаемые методы Compute

### Управление нодами
| Метод | Поддержка |
| --- | --- |
|create_node| #7 |
|deploy_node| :heavy_minus_sign: |
|destroy_node| #8 |
|features| |
|list_nodes| :heavy_check_mark:|
|reboot_node| #17 |
|start_node| #11 |
|stop_node| #11 |
|wait_until_running| :heavy_minus_sign: |

### Управление образами
| Метод | Поддержка |
| --- | --- |
|copy_image| |
|create_image| |
|delete_image| |
|get_image| |
|list_images| #4 |


### Управление дисками
| Метод | Поддержка |
| --- | --- |
|attach_volume| |
|create_volume_snapshot| |
|create_volume| |
|destroy_volume_snapshot| |
|destroy_volume| |
|detach_volume| |
|list_volume_snapshots| |
|list_volumes| |

### Управление SSH ключами
| Метод | Поддержка |
| --- | --- |
|create_key_pair| #3 |
|delete_key_pair| #2 |
|get_key_pair| :heavy_check_mark: |
|import_key_pair_from_file| :heavy_minus_sign: |
|import_key_pair_from_string| :heavy_minus_sign: |
|list_key_pairs| :heavy_check_mark: |

### Остальные
| Метод | Поддержка |
| --- | --- |
|list_locations| #5 |
|list_sizes| #6 |



## Методы DNS
| Метод | Поддержка |
| --- | --- |
|create record| #19 |
|create zone| :heavy_check_mark: |
|delete record| #22 |
|delete zone| #21 |
|list records| #26 |
|list zones| :heavy_check_mark: |
|list_record_types||
|get_record|#23|
|get_zone|#24|
|update record| #27 |
|update zone| #28 |
| export_zone_to_bind_format | |
|export_zone_to_bind_zone_file ||

# Документация к API
https://developers.vscale.io/documentation/api/v1/

## Разработка

В проекте настроена автоматическая проверка линтерами и тестами.

Линтеры запускаются в `pre-commit`, тесты в `pytest`.
