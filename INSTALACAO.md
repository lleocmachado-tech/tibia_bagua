# Remontar o ambiente do zero

Este repositório guarda as ferramentas, a documentação e — nesta pasta
`configuracoes/` — **as correções e ajustes que fazem o conjunto funcionar**.
O servidor, o cliente e os assets vêm de fora (veja o [README](README.md)).

Este documento é a ordem de montagem. Sem ele, refazer significa redescobrir na
marra cada um dos problemas listados em [LEIA-ME.md](LEIA-ME.md).

---

## Pré-requisitos

- Windows 10/11
- XAMPP (MariaDB) em `C:\xampp`
- Visual Studio Build Tools com **toolset v145** (VS 2026) — a v144/VS2022 dá
  `LNK2019: unresolved external symbol __std_rotate`
- Go (para o login-server), Node 18+ e Rust 1.77+ (só para o editor de assets)

---

## 1. Banco de dados

```bash
C:\xampp\mysql\bin\mysqld.exe --defaults-file=C:\xampp\mysql\bin\my.ini --standalone
```

```sql
CREATE DATABASE otserv;
```

```bash
mysql -u root -h 127.0.0.1 otserv < schema.sql
mysql -u root -h 127.0.0.1 otserv < configuracoes/sql/criar-conta-admin.sql
```

O `schema.sql` vem junto do Canary. O segundo cria a conta `admin` / `admin123`
com o personagem **Admin** (level 100, group 6).

---

## 2. Canary (servidor)

Clone em um caminho **sem acentos**:

```bash
git clone https://github.com/opentibiabr/canary C:\dev\canary
```

> **Por quê sem acento:** dentro de `Área de Trabalho` o vcpkg falha ao baixar
> ferramentas (`Abnormal exit ... no such file or directory`). Foi um bug real.

Compile com o **vcvars64.bat do VS 2026** (não o do 2022) — veja
`ferramentas/build_canary.bat`.

Depois copie o binário e o datapack para `C:\dev\canary_run\` e ajuste o
`config.lua`. Os valores que importam estão em
`configuracoes/canary-config-essencial.txt`.

---

## 3. OTClient (cliente)

```bash
git clone https://github.com/mehah/otclient
```

Aplique o patch:

```bash
git apply configuracoes/patches/otclient.patch
```

Ele faz duas coisas:
- `init.lua`: aponta a lista de servidores para `127.0.0.1:8088`
- `characterlist.lua`: adiciona o gancho `autoEnterGame`, que entra no mundo
  automaticamente **uma vez por sessão** (one-shot, para não prender você num
  loop ao deslogar)

### Assets 15.25 — o ponto crítico

O cliente precisa dos assets **15.25**, não 15.11. Instale-os em
`otclient-src/data/things/1525/`.

> **A causa raiz do jogo não abrir:** a partir de 1520 o `level percent` virou
> `u16`. Um cliente 15.11 lê `u8` e todo o pacote desalinha depois desse byte.
> O Canary só aceita 1525, 1100 e 860.

Confirmação de que casam: o `appearances.dat` do servidor e o do cliente têm
exatamente **4.862.287 bytes**.

### Perfil do cliente

Copie `configuracoes/otclient-config.otml` para `C:\dev\otcprofile\config.otml`
e inicie sempre com:

```
otclient.exe --user-dir=C:/dev/otcprofile
```

> O perfil padrão em `%APPDATA%\otcr\` travava numa tela de seleção de idioma
> ignorando o `config.otml`. Nunca descobri a causa; o `--user-dir` contorna.

---

## 4. login-server

```bash
git clone https://github.com/opentibiabr/login-server
git apply configuracoes/patches/login-server-database-go.patch
go build -o login-server-new.exe ./src
```

Copie `configuracoes/login-server.env.example` para `.env`.

Dois detalhes que quebram silenciosamente:
- Sem `allowNativePasswords` na DSN, o driver Go recusa a senha vazia do MySQL
  com `Access denied ... using password: YES` — é o que o patch corrige
- `SERVER_NAME` no `.env` tem que ser **idêntico** ao `serverName` do
  `config.lua`, senão dá `SERVER_NAME_MISMATCH (LS-1001)`

---

## 5. Editores (opcional)

| Ferramenta | Origem |
|---|---|
| Canary's Map Editor 4.0 | [opentibiabr/remeres-map-editor](https://github.com/opentibiabr/remeres-map-editor) |
| Canary Studio | [beats-dh/Beats-Assets-Editor](https://github.com/beats-dh/Beats-Assets-Editor) — compilar com `ferramentas/build_beats.bat` |
| LibreSprite | [LibreSprite/LibreSprite](https://github.com/LibreSprite/LibreSprite) |

### Pasta de assets para os editores

Os dois editores esperam uma raiz de cliente com `assets/` + `package.json`,
formato que o OTClient não usa. Monte assim:

```
C:\dev\tools\rme-assets\
  package.json     ->  { "version": "15.25" }
  assets\          ->  junction para otclient-src\data\things\1525
```

```powershell
New-Item -ItemType Junction -Path "C:\dev\tools\rme-assets\assets" `
         -Value "<...>\otclient-src\data\things\1525"
```

### Configuração do editor de mapa

```bash
reg import configuracoes\editor-mapa.reg
```

Isso restaura, em `HKCU\Software\OpenTibiaBR\Canary Map Editor`:
- caminho dos assets 15.25
- pastas de monstros e NPCs
- **posição inicial no templo de Thais** (`32369:32241:7`) — sem isso ele abre
  numa coordenada vazia, com a tela toda preta, o que parece erro mas não é

---

## 6. Conferir

```bash
JOGAR.bat
```

O log do Canary deve mostrar:

```
Admin has logged in. (Protocol: 1525, Profile: current)
```

Se der `ERRO 10061`, o cliente abriu antes do servidor terminar de carregar —
feche tudo e rode de novo.

---

## O que este repositório NÃO reconstrói sozinho

Com honestidade, para você saber o tamanho do trabalho se precisar refazer:

| Item | Origem |
|---|---|
| Código do Canary, OTClient e login-server | clone dos repositórios upstream |
| Assets 15.25 (136 MB) | o próprio cliente baixa |
| Mapa `otservbr.otbm` (176 MB) | vem com o datapack do Canary |
| Compilação do Canary | ~40 min na primeira vez (vcpkg) |
| Compilação do Canary Studio | ~25 min (`lto = "fat"`) |
| Personagens criados depois | só existem no banco — use `mysqldump` |

O que está versionado aqui são os **patches, configs e o conhecimento** — a parte
que levou horas para descobrir e que não se baixa de lugar nenhum.
