Endpoints estão disponíveis em `src/trabalho_g2/telemetry/controller.py` e `src/trabalho_g2/telemetry/websockets.py`

Frontend deve ser cadastrado no reverse_proxy do `Caddyfile`, também ter um Dockerfile dentro de `frontend/Dockerfile`, e ser cadastrado no `docker-compose.yml`

Usar imagem `ngnix` para container do frontend.

Qualquer porta (disponível) pode ser usada para rodar o frontend dentro da rede do docker.
