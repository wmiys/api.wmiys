CREATE TABLE `Products` (
  `id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
  `user_id` INT(10) UNSIGNED NOT NULL,
  `name` VARCHAR(250) COLLATE UTF8_UNICODE_CI DEFAULT NULL,
  `description` TEXT COLLATE UTF8_UNICODE_CI,
  `product_categories_sub_id` INT(10) UNSIGNED DEFAULT NULL,
  `location_id` INT(10) UNSIGNED DEFAULT NULL,
  `dropoff_distance` SMALLINT(5) UNSIGNED DEFAULT '20',
  `price_full` DECIMAL(10,2) UNSIGNED DEFAULT NULL,
  `price_half` DECIMAL(10,2) UNSIGNED DEFAULT NULL,
  `image` CHAR(41) COLLATE UTF8_UNICODE_CI DEFAULT NULL,
  `minimum_age` TINYINT(3) UNSIGNED DEFAULT NULL,
  `created_on` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `user_id` (`user_id`),
  CONSTRAINT `Products_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `Users` (`id`) ON UPDATE CASCADE
) ENGINE=INNODB DEFAULT CHARSET=UTF8 COLLATE=UTF8_UNICODE_CI;


-- #147
ALTER TABLE Products DROP COLUMN price_half;
