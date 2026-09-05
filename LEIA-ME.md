# TIBIA BAGUA — servidor local funcionando

## Atalhos

| Arquivo | O que faz |
|---|---|
| `JOGAR.bat` | Sobe o servidor e entra no jogo |
| `EDITOR-MAPA.bat` | Abre o editor de mapa, já no templo de Thais |
| `EDITOR-SPRITE.bat` | Abre o editor de assets + o editor de pixel art |
| `REFERENCIA-MONSTROS.html` | Busca: nome do monstro/NPC → LookType (nº do outfit) |
| `BACKUP.bat` | Snapshot com data/hora do mapa e dos assets |
| `RESTAURAR.bat` | Escolhe um backup da lista e volta tudo |
| `GUIA-EDICAO.pdf` | Guia ilustrado, passo a passo |
| `EDITORES.md` | Referência rápida dos editores |

## Como jogar

Dê duplo clique em **`JOGAR.bat`** (na raiz desta pasta).

Ele sobe MySQL → Canary → login-server → abre o cliente, e o personagem
**Admin** entra no mundo automaticamente.

- Conta: `admin`
- Senha: `admin123`
- Personagem: `Admin` (level 100)

Na primeira tela dentro do jogo aparece a janela "Customise Character"
(escolha de outfit). É normal — clique em **Ok** ou **Cancel** e jogue.

Tudo roda em `127.0.0.1`. Nada é exposto para fora do computador.

---

## Qual era o problema (e por que só agora funcionou)

O login por HTTP sempre funcionou. O que quebrava era a **entrada no mundo**.

A causa raiz era uma **incompatibilidade de versão de protocolo**:

| | Versão |
|---|---|
| Canary (servidor) — `src/core.hpp` → `CLIENT_VERSION` | **1525** (15.25) |
| OTClient (cliente) — assets instalados | **1511** (15.11) |

O Canary só aceita três protocolos: `1525`, `1100` e `860`
(`ProtocolProfileRegistry::resolveGameLoginLayout`). Com o cliente em 1511 a
conexão era recusada de um jeito que o cliente nem conseguia interpretar.

Pior: mesmo forçando a conexão, **1511 e 1525 não são compatíveis no fio**.
Em `modules/game_features/features.lua` existem mudanças reais de formato
acima de 1511 — a decisiva é:

```lua
if version >= 1520 then
    g_game.enableFeature(GameLevelPercentU16)   -- level percent vira u16
```

O servidor 15.25 manda o percentual de level como **u16**; um cliente 15.11 lê
**u8**. A partir desse byte todo o resto do pacote desalinha — era exatamente
isso que produzia os erros de "invalid item id" e "invalid packet size".

### A correção

1. Baixei e instalei os assets **15.25** do cliente em
   `TIBIA BAGUA/otclient-src/data/things/1525/` (release `15.25.0a00a0`).
   Confirmação de que casa com o servidor: o `appearances.dat` do Canary e o do
   cliente têm **exatamente 4.862.287 bytes** — é o mesmo asset set.
2. Apontei o cliente para protocolo **1525** (`client-version` e `ServerList`).
3. **Revertí os patches em C++ da sessão anterior.** Eles estavam errados:
   forçavam checksum ADLER32, mas o OTClient habilita
   `GameSequencedPackets` a partir de 1290 — ou seja, usa **SEQUENCE**, que já
   era o comportamento original do Canary. O código-fonte voltou ao estado
   original (`git checkout`) e foi recompilado.

Ou seja: o problema nunca esteve na camada de checksum/framing do Canary —
estava na versão do cliente.

---

## O que ficou alterado

| Arquivo | Mudança |
|---|---|
| `JOGAR.bat` | **novo** — sobe tudo e abre o jogo |
| `otclient-src/data/things/1525/` | **novo** — assets 15.25 (6038 arquivos) |
| `otclient-src/modules/client_entergame/characterlist.lua` | hook `autoEnterGame` (entra no mundo sozinho, uma vez por sessão) |
| `C:\dev\otcprofile\config.otml` | perfil do cliente (protocolo 1525, autologin) |
| `login-server-src/.env` | `SERVER_PATH` + `SERVER_NAME` |
| `login-server-src/src/configs/database.go` | DSN com `allowNativePasswords` |
| `C:\dev\canary` | código-fonte do Canary (sem modificações locais) |
| `C:\dev\canary_run` | servidor em execução (binário recompilado) |

O cliente é iniciado com `--user-dir=C:/dev/otcprofile` para usar um perfil
previsível. Se quiser voltar ao perfil padrão, é só abrir `otclient.exe` direto —
a mesma configuração também foi copiada para
`%APPDATA%\otcr\otclient\otclient\config.otml`.

Para não entrar no mundo automaticamente, mude `autoEnterGame` para `false` em
`C:\dev\otcprofile\config.otml`.

---

## Se algo não subir

Erro `10061` (conexão recusada) = o cliente abriu antes do servidor terminar de
carregar. Feche tudo e rode o `JOGAR.bat` de novo — ele espera ~28s pelo Canary.

Portas usadas: `3306` (MySQL), `7171`/`7172` (Canary), `8088` (login-server).
