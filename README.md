libcloud драйвер для сервиса vscale.io.

## Поддерживаемые методы Compute
| Метод | Поддержка |
| --- | --- |
|attach_volume| |
|copy_image| |
|create_image| |
|create_key_pair| #3 |
|create_node|#7|
|create_volume| |
|create_volume_snapshot| |
|delete_image| |
|delete_key_pair| #2 |
|deploy_node| :heavy_minus_sign: |
|destroy_node| #8 |
|destroy_volume| |
|destroy_volume_snapshot| |
|detach_volume| |
|features| |
|get_image| |
|get_key_pair|:heavy_check_mark:|
|import_key_pair_from_file| :heavy_minus_sign: |
|import_key_pair_from_string| :heavy_minus_sign: |
|list_images| :heavy_exclamation_mark: #4 |
|list_key_pairs| :heavy_check_mark:|
|list_locations| :heavy_exclamation_mark: #5 |
|list_nodes| :heavy_check_mark:|
|list_sizes| :heavy_exclamation_mark: #6 |
|list_volume_snapshots| |
|list_volumes| |
|reboot_node| :heavy_minus_sign: |
|start_node| :heavy_minus_sign: |
|stop_node| :heavy_minus_sign: |
|wait_until_running| |


## Методы DNS
| Метод | Поддержка |
| --- | --- |
|list zones| |
|list records| |
|create zone| |
|update zone| |
|create record| |
|update record| |
|delete zone| |
|delete record| |

# Документация к API
https://developers.vscale.io/documentation/api/v1/

## Разработка

В проекте настроена автоматическая проверка линтерами и тестами.

Линтеры запускаются в `pre-commit`, тесты в `pytest`.
