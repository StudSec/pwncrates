import re
import sqlite3
# Open the backup.sql file
bckup = open("backup.sql", "r")
sqlitecon = sqlite3.connect("../data/db/pwncrates.db")
# Read the file
bckup = bckup.read()
# Split the file into a list of queries
bckup = bckup.split(";")
"""

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `oauth_id` int(11) DEFAULT NULL,
  `name` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `email` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `type` varchar(80) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `secret` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `website` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `affiliation` varchar(128) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `country` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `bracket` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `hidden` tinyint(1) DEFAULT NULL,
  `banned` tinyint(1) DEFAULT NULL,
  `verified` tinyint(1) DEFAULT NULL,
  `team_id` int(11) DEFAULT NULL,
  `created` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`),
  UNIQUE KEY `id` (`id`,`oauth_id`),
  UNIQUE KEY `oauth_id` (`oauth_id`),
  KEY `team_id` (`team_id`),
  CONSTRAINT `users_ibfk_1` FOREIGN KEY (`team_id`) REFERENCES `teams` (`id`),
  CONSTRAINT `CONSTRAINT_1` CHECK (`hidden` in (0,1)),
  CONSTRAINT `CONSTRAINT_2` CHECK (`banned` in (0,1)),
  CONSTRAINT `CONSTRAINT_3` CHECK (`verified` in (0,1))
) ENGINE=InnoDB AUTO_INCREMENT=107 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
"""
# For each of the values inserted into the users table, print the email address
for j in range(1, len(bckup)):
    print(bckup[j])
    print("----------------")
    if bckup[j].startswith("\nINSERT INTO `users` VALUES"):
        # Get every string within brackets
        email = re.findall(r'\((.*?)\)', bckup[j])
        for e in email:
            username = e.split(",")[2]
            password = e.split(",")[3]
            email = e.split(",")[4]
            university = e.split(",")[8]
            # INSERT INTO USERS NULL, name, password, university, 0

            sqlitecon.execute("INSERT INTO users VALUES (NULL, ?, ?, ?, 0)", (username, password, university))
            
