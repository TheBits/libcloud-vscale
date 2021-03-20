libcloud драйвер для сервиса vscale.io.

## Поддерживаемые методы Compute
| Метод | Поддержка |
| --- | --- |
|attach_volume||
|copy_image||
|create_image||
|create_key_pair|#3|
|create_node|#7|
|create_volume||
|create_volume_snapshot||
|delete_image||
|delete_key_pair|#2|
|deploy_node|-|
|destroy_node|#8|
|destroy_volume||
|destroy_volume_snapshot||
|detach_volume||
|features||
|get_image||
|get_key_pair|№9|
|import_key_pair_from_file|-|
|import_key_pair_from_string|-|
|list_images|#4|
|list_key_pairs|+|
|list_locations|#5|
|list_nodes|-|
|list_sizes|#6|
|list_volume_snapshots||
|list_volumes||
|reboot_node|-|
|start_node|-|
|stop_node|-|
|wait_until_running||


## Методы DNS
| Метод | Поддержка |
| --- | --- |
|list zones||
|list records||
|create zone||
|update zone||
|create record||
|update record||
|delete zone||
|delete record||


## Разработка

В проекте настроена автоматическая проверка линтерами и тестами.

Линтеры запускаются в `pre-commit`, тесты в `pytest`.
