-- Cria a conta e o personagem usados pelo JOGAR.bat.
-- Rode DEPOIS de importar o schema.sql do Canary:
--   mysql -u root -h 127.0.0.1 otserv < schema.sql
--   mysql -u root -h 127.0.0.1 otserv < criar-conta-admin.sql
--
-- Conta.....: admin
-- Senha.....: admin123   (guardada como SHA1)
-- Personagem: Admin      (level 100, group 6 = god)

INSERT INTO `accounts` (`name`, `email`, `password`, `type`)
VALUES (
  'admin',
  'admin@localhost.test',
  SHA1('admin123'),   -- f865b53623b121fd34ee5426c792e5c33af8c227
  6                   -- 6 = god
)
ON DUPLICATE KEY UPDATE
  `email` = VALUES(`email`),
  `password` = VALUES(`password`),
  `type` = VALUES(`type`);

SET @acc := (SELECT `id` FROM `accounts` WHERE `name` = 'admin' LIMIT 1);

INSERT INTO `players`
  (`name`, `group_id`, `account_id`, `level`, `vocation`, `town_id`,
   `posx`, `posy`, `posz`, `health`, `healthmax`, `mana`, `manamax`, `looktype`)
VALUES
  ('Admin', 6, @acc, 100, 0, 2,
   32058, 31886, 6, 185, 185, 0, 0, 136)
ON DUPLICATE KEY UPDATE
  `group_id` = VALUES(`group_id`),
  `account_id` = VALUES(`account_id`),
  `level` = VALUES(`level`);

-- Conferir:
SELECT a.name AS conta, p.name AS personagem, p.level, p.town_id
FROM accounts a JOIN players p ON p.account_id = a.id
WHERE a.name = 'admin';
