CREATE TABLE `Locations_States` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `state_id` CHAR(2) COLLATE UTF8_UNICODE_CI NOT NULL,
  `name` CHAR(50) COLLATE UTF8_UNICODE_CI NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  UNIQUE KEY `state_id` (`state_id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=INNODB DEFAULT CHARSET=UTF8 COLLATE=UTF8_UNICODE_CI;