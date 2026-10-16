# Arquitetura

`health_demo/pipeline.py` gera registros fictícios, valida referências, simula preparação, envio e consulta. A decisão final é registrada por item. `build_snapshot()` reconcilia totais por serviço e cria três entradas no ledger: Gerar, Enviar e Consultar. `python -m health_demo` exporta o JSON consumido pela página estática.

`ensure_writable(environment)` é um guard demonstrativo: somente `sandbox` permite construir a execução simulada. Não existe adaptador de rede, conexão a banco ou caminho para escrita real.

O site lê o snapshot e filtra apenas a tabela de controle. Os indicadores sempre representam a execução completa. O pipeline usa biblioteca padrão Python; o site usa HTML, CSS e JavaScript.

## Limites

A execução apresentada é uma simulação concluída e reproduzível; a página não inicia trabalhos de migração. Um sistema real exige autenticação, persistência transacional, auditoria protegida, controle de cancelamento, política de retry, limitação de chamadas e contratos de API homologados.
