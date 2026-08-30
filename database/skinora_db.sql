-- MySQL dump 10.13  Distrib 8.0.46, for Win64 (x86_64)
--
-- Host: localhost    Database: skinora_db
-- ------------------------------------------------------
-- Server version	8.0.46

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `checkin_notifications`
--

DROP TABLE IF EXISTS `checkin_notifications`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `checkin_notifications` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `tracking_id` int NOT NULL,
  `due_at` datetime NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `resolved_at` datetime DEFAULT NULL,
  `is_resolved` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `user_id` (`user_id`),
  KEY `tracking_id` (`tracking_id`),
  CONSTRAINT `checkin_notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`),
  CONSTRAINT `checkin_notifications_ibfk_2` FOREIGN KEY (`tracking_id`) REFERENCES `tracking` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `checkin_notifications`
--

LOCK TABLES `checkin_notifications` WRITE;
/*!40000 ALTER TABLE `checkin_notifications` DISABLE KEYS */;
INSERT INTO `checkin_notifications` VALUES (1,2,14,'2026-08-23 18:09:03','2026-08-16 12:58:09','2026-08-16 18:31:03',1),(2,10,15,'2026-08-23 18:50:54','2026-08-16 13:21:02','2026-08-16 18:51:22',1),(3,10,17,'2026-08-29 21:52:43','2026-08-22 16:23:01','2026-08-22 21:53:47',1),(4,10,18,'2026-08-29 22:07:30','2026-08-22 16:37:42','2026-08-22 22:09:27',1),(5,2,1,'2026-08-23 17:02:24','2026-08-23 11:38:13','2026-08-23 19:26:42',1),(6,10,15,'2026-08-23 18:51:22','2026-08-23 15:30:30','2026-08-25 20:27:55',1),(7,10,20,'2026-09-01 20:06:57','2026-08-25 14:44:08','2026-08-25 20:27:55',1),(8,10,21,'2026-09-01 20:46:43','2026-08-25 15:16:53','2026-08-25 20:47:58',1),(9,10,22,'2026-09-02 13:20:59','2026-08-26 07:51:15','2026-08-26 13:22:28',1),(10,10,16,'2026-08-27 20:29:37','2026-08-28 03:41:16','2026-08-28 18:35:06',1),(11,10,24,'2026-09-04 18:53:52','2026-08-28 13:24:06','2026-08-28 18:54:42',1),(12,10,25,'2026-09-04 23:19:21','2026-08-28 17:51:14','2026-08-28 23:28:29',1),(13,10,17,'2026-08-29 21:53:47','2026-08-29 16:43:08','2026-08-29 23:04:52',1),(14,14,26,'2026-09-28 23:12:23','2026-08-29 17:42:36','2026-08-29 23:12:55',1),(15,10,18,'2026-08-29 22:42:11','2026-08-29 17:43:07',NULL,0),(16,14,27,'2026-09-06 12:58:55','2026-08-30 07:29:15','2026-08-30 12:59:37',1),(17,2,1,'2026-08-30 17:08:13','2026-08-30 12:25:51',NULL,0),(18,2,14,'2026-08-30 19:26:42','2026-08-30 14:25:53',NULL,0);
/*!40000 ALTER TABLE `checkin_notifications` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `condition_remedies`
--

DROP TABLE IF EXISTS `condition_remedies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `condition_remedies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `final_condition` varchar(50) NOT NULL,
  `remedy_id` int NOT NULL,
  `sort_order` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_condition_remedy` (`final_condition`,`remedy_id`),
  KEY `fk_cr_remedy` (`remedy_id`),
  CONSTRAINT `fk_cr_remedy` FOREIGN KEY (`remedy_id`) REFERENCES `remedies` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=33 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `condition_remedies`
--

LOCK TABLES `condition_remedies` WRITE;
/*!40000 ALTER TABLE `condition_remedies` DISABLE KEYS */;
INSERT INTO `condition_remedies` VALUES (1,'Dry_Acne',1,1),(2,'Dry_Acne',2,2),(3,'Dry_Acne',3,3),(4,'Oily_Acne',1,1),(5,'Oily_Acne',4,2),(6,'Oily_Acne',2,3),(7,'Normal_Acne',1,1),(8,'Normal_Acne',2,2),(9,'Normal_Acne',4,3),(10,'Dry_NoAcne',3,1),(11,'Dry_NoAcne',5,2),(12,'Dry_NoAcne',1,3),(13,'Oily_NoAcne',4,1),(14,'Oily_NoAcne',6,2),(15,'Oily_NoAcne',1,3),(16,'Normal_NoAcne',7,1),(17,'Normal_NoAcne',1,2),(18,'Normal_NoAcne',2,3),(19,'Dry_Acne',10,4),(20,'Dry_Acne',11,5),(21,'Dry_NoAcne',8,4),(22,'Dry_NoAcne',9,5),(23,'Dry_NoAcne',20,6),(24,'Normal_Acne',18,4),(25,'Normal_Acne',19,5),(26,'Normal_NoAcne',16,4),(27,'Normal_NoAcne',17,5),(28,'Normal_NoAcne',20,6),(29,'Oily_Acne',12,4),(30,'Oily_Acne',13,5),(31,'Oily_NoAcne',14,4),(32,'Oily_NoAcne',15,5);
/*!40000 ALTER TABLE `condition_remedies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detections`
--

DROP TABLE IF EXISTS `detections`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detections` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `image_url` text,
  `skin_type` enum('Dry','Oily','Normal') NOT NULL,
  `skin_type_confidence` float NOT NULL,
  `acne_status` enum('Acne','NoAcne') NOT NULL,
  `acne_confidence` float NOT NULL,
  `final_condition` varchar(50) NOT NULL,
  `routing` enum('direct','questionnaire','consultant') NOT NULL DEFAULT 'direct',
  `detected_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_detections_user` (`user_id`),
  CONSTRAINT `fk_detections_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=98 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detections`
--

LOCK TABLES `detections` WRITE;
/*!40000 ALTER TABLE `detections` DISABLE KEYS */;
INSERT INTO `detections` VALUES (1,2,'https://res.cloudinary.com/wihktw8b/image/upload/v1783254218/skinora/uploads/yiizuh6ebwwbsl1gwum6.jpg','Dry',0.9992,'NoAcne',0.9986,'Dry_NoAcne','direct','2026-07-05 12:23:39'),(2,2,'https://res.cloudinary.com/wihktw8b/image/upload/v1783257243/skinora/uploads/htdmrqab9r4ebyqe0jqr.jpg','Dry',0.9988,'NoAcne',0.9536,'Dry_NoAcne','direct','2026-07-05 13:14:06'),(3,2,'https://res.cloudinary.com/wihktw8b/image/upload/v1783257291/skinora/uploads/zuqtsfxeabv1kplbzknj.jpg','Normal',0.8984,'NoAcne',0.9795,'Normal_NoAcne','direct','2026-07-05 13:14:52'),(4,2,'https://res.cloudinary.com/wihktw8b/image/upload/v1783257333/skinora/uploads/boaiv1axcgux9sopr4en.jpg','Oily',0.6703,'NoAcne',0.9987,'Oily_NoAcne','questionnaire','2026-07-05 13:15:34'),(5,2,'https://res.cloudinary.com/wihktw8b/image/upload/v1783257391/skinora/uploads/tjcw51kke3y68mojpwux.jpg','Normal',0.9375,'NoAcne',0.9991,'Normal_NoAcne','direct','2026-07-05 13:16:32'),(6,2,'https://res.cloudinary.com/wihktw8b/image/upload/v1783257426/skinora/uploads/s8daipnwyepdhrl5rbx7.jpg','Dry',0.763,'NoAcne',0.9959,'Dry_NoAcne','direct','2026-07-05 13:17:11'),(7,2,'https://res.cloudinary.com/wihktw8b/image/upload/v1783257562/skinora/uploads/tdqzazhj4iuultpc01je.jpg','Oily',0.9909,'Acne',0.9993,'Oily_Acne','direct','2026-07-05 13:19:23'),(35,2,'https://res.cloudinary.com/wihktw8b/image/upload/v1786883919/skinora/uploads/datikb2xfbbyhnxuqy84.jpg','Dry',0.8069,'Acne',0.9987,'Dry_Acne','direct','2026-08-16 12:38:40'),(36,2,'https://res.cloudinary.com/wihktw8b/image/upload/v1786885262/skinora/uploads/jjxf1bw4adudwbmkrqzk.jpg','Dry',0.935,'Acne',0.9997,'Dry_Acne','direct','2026-08-16 13:01:03'),(37,2,'https://res.cloudinary.com/wihktw8b/image/upload/v1786885400/skinora/uploads/coyzttpwmz3zxslnrr4h.jpg','Dry',0.8804,'Acne',1,'Dry_Acne','direct','2026-08-16 13:03:21'),(38,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1786886377/skinora/uploads/a9y25em7wfjt1wtfhh7e.jpg','Normal',0.8553,'Acne',1,'Normal_Acne','direct','2026-08-16 13:19:39'),(39,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1786886420/skinora/uploads/k1rsqfg4sj7ssm2ig2ak.jpg','Dry',0.7243,'NoAcne',0.965,'Dry_NoAcne','direct','2026-08-16 13:20:21'),(40,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1786886437/skinora/uploads/jaqgrdalwoqp7cmgm8cw.jpg','Dry',0.7243,'NoAcne',0.965,'Dry_NoAcne','direct','2026-08-16 13:20:38'),(41,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1786886480/skinora/uploads/x9b2oim3fcquvohk3atx.jpg','Normal',0.8553,'Acne',1,'Normal_Acne','direct','2026-08-16 13:21:22'),(42,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787237853/skinora/uploads/kq5bvoguzuthxis5zjnd.jpg','Normal',0.8553,'Acne',1,'Normal_Acne','direct','2026-08-20 14:57:34'),(43,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787415730/skinora/uploads/jd3ipgqot19rl6pamug9.jpg','Normal',0.9988,'Acne',0.9921,'Normal_Acne','direct','2026-08-22 16:22:11'),(44,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787415825/skinora/uploads/ytyitez5ier0bwoo3t5c.jpg','Normal',0.9847,'Acne',0.9984,'Normal_Acne','direct','2026-08-22 16:23:47'),(45,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787416638/skinora/uploads/wxtaqtrff4rth7qbiup2.jpg','Normal',0.9926,'NoAcne',0.9985,'Normal_NoAcne','direct','2026-08-22 16:37:19'),(46,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787416766/skinora/uploads/rnk1hmn0bvkccqvx7dnp.jpg','Normal',0.6548,'Acne',0.5792,'Normal_Acne','questionnaire','2026-08-22 16:39:27'),(47,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787418730/skinora/uploads/fxqcbc9et80vx82rjtrw.jpg','Normal',0.489,'NoAcne',1,'Normal_NoAcne','questionnaire','2026-08-22 17:12:11'),(48,2,'https://res.cloudinary.com/wihktw8b/image/upload/v1787493400/skinora/uploads/zrbajm7m0cgqt6xuliij.jpg','Normal',0.9767,'Acne',0.9643,'Normal_Acne','direct','2026-08-23 13:56:42'),(49,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787587105/skinora/uploads/ymxzxthctv8cxhyslqjg.jpg','Dry',0.7115,'NoAcne',1,'Dry_NoAcne','direct','2026-08-24 15:58:26'),(50,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787666517/skinora/uploads/g9t1kwipq4g8ltizmttd.jpg','Normal',0.9897,'NoAcne',0.9553,'Normal_NoAcne','direct','2026-08-25 14:01:58'),(51,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787669874/skinora/uploads/jroeffc3uknsbfrsj6ok.jpg','Normal',0.8417,'NoAcne',0.94,'Normal_NoAcne','direct','2026-08-25 14:57:55'),(52,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787670931/skinora/uploads/k7fznqiq6o8oplbjxbbm.jpg','Oily',0.5292,'Acne',0.8622,'Oily_Acne','questionnaire','2026-08-25 15:15:32'),(53,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787670974/skinora/uploads/ytahnwzblktty7xzburr.jpg','Dry',0.7394,'Acne',0.9988,'Dry_Acne','direct','2026-08-25 15:16:15'),(54,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787671077/skinora/uploads/ncddr3prditycavkptzb.jpg','Normal',0.9897,'NoAcne',0.9553,'Normal_NoAcne','direct','2026-08-25 15:17:58'),(55,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787675751/skinora/uploads/zyfdywpnkyxywqpn752o.jpg','Normal',0.8417,'NoAcne',0.94,'Normal_NoAcne','direct','2026-08-25 16:35:53'),(56,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787719034/skinora/uploads/ic2glku4n8jcuspdwloy.jpg','Dry',0.7394,'Acne',0.9988,'Dry_Acne','direct','2026-08-26 04:37:16'),(57,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787730581/skinora/uploads/dp7v4rn4ra26iforqcip.jpg','Dry',0.7394,'Acne',0.9988,'Dry_Acne','direct','2026-08-26 07:49:43'),(58,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787730746/skinora/uploads/h22rlumdtmez2qowbq2t.jpg','Normal',0.9897,'NoAcne',0.9553,'Normal_NoAcne','direct','2026-08-26 07:52:28'),(59,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787922305/skinora/uploads/axlfdyxee2crhxoevjrr.jpg','Dry',0.5058,'Acne',0.9795,'Dry_Acne','questionnaire','2026-08-28 13:05:06'),(60,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787922354/skinora/uploads/gjxdylgwkv0ctnq9hfgs.jpg','Dry',0.5058,'Acne',0.9795,'Dry_Acne','questionnaire','2026-08-28 13:05:55'),(61,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787922371/skinora/uploads/b4xax14zdpkgdfetpnm3.jpg','Dry',0.5058,'Acne',0.9795,'Dry_Acne','questionnaire','2026-08-28 13:06:12'),(62,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787923313/skinora/uploads/bc5vve6oglyqiwzfgrgb.jpg','Dry',0.6049,'Acne',0.9998,'Dry_Acne','questionnaire','2026-08-28 13:21:55'),(63,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787923393/skinora/uploads/ra18j3hdeykjwvkoimum.jpg','Dry',0.9811,'NoAcne',1,'Dry_NoAcne','direct','2026-08-28 13:23:14'),(64,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787923480/skinora/uploads/mukbbeagot4i6v3suc0n.jpg','Dry',0.9865,'NoAcne',1,'Dry_NoAcne','direct','2026-08-28 13:24:42'),(65,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787923520/skinora/uploads/pbbgan5a19nzlbcf7z6s.jpg','Normal',0.9709,'NoAcne',0.9916,'Normal_NoAcne','direct','2026-08-28 13:25:21'),(66,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787938899/skinora/uploads/g3unl27pfmreoehqamdo.jpg','Dry',0.4874,'Acne',1,'Dry_Acne','questionnaire','2026-08-28 17:41:40'),(67,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787938932/skinora/uploads/ktfvm5dloeyyfcemcxih.jpg','Dry',0.6701,'Acne',0.9969,'Dry_Acne','direct','2026-08-28 17:42:14'),(68,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1787939908/skinora/uploads/pfbkl4ypfel9l8e5hfog.jpg','Dry',0.5261,'Acne',0.999,'Dry_Acne','questionnaire','2026-08-28 17:58:29'),(69,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788020942/skinora/uploads/ddvkhd2ibexhjuar0kf1.jpg','Dry',0.5876,'Acne',0.9782,'Dry_Acne','questionnaire','2026-08-29 16:29:03'),(70,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788021074/skinora/uploads/i9c63litetad2xm4dk6e.jpg','Normal',0.7874,'Acne',1,'Normal_Acne','direct','2026-08-29 16:31:15'),(71,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788021125/skinora/uploads/vjo5r6zdp7os4hr9a2j1.jpg','Normal',0.6662,'Acne',0.9597,'Normal_Acne','direct','2026-08-29 16:32:06'),(72,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788021238/skinora/uploads/a7uh2utudzjghydpyp5y.jpg','Oily',0.5693,'Acne',0.7717,'Oily_Acne','questionnaire','2026-08-29 16:33:59'),(73,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788021305/skinora/uploads/wapxvivikd6eznjveor4.jpg','Normal',0.4545,'Acne',0.9794,'Normal_Acne','questionnaire','2026-08-29 16:35:06'),(74,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788021353/skinora/uploads/ysx7tyyvy8k8gu4uqdce.jpg','Dry',0.4464,'Acne',0.9977,'Dry_Acne','questionnaire','2026-08-29 16:35:54'),(75,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788021394/skinora/uploads/mo3gh9w02wb5bexunntd.jpg','Normal',0.4422,'Acne',0.9734,'Normal_Acne','questionnaire','2026-08-29 16:36:35'),(76,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788021451/skinora/uploads/abhps0mhvmkl3sgk7i3v.jpg','Oily',0.9732,'NoAcne',1,'Oily_NoAcne','direct','2026-08-29 16:37:32'),(77,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788022099/skinora/uploads/bed3li5pdmkijqsgvqwo.jpg','Oily',0.9738,'NoAcne',1,'Oily_NoAcne','direct','2026-08-29 16:48:21'),(78,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788022196/skinora/uploads/vj0vflkn2rqlm0eusw4i.jpg','Normal',0.4422,'Acne',0.9734,'Normal_Acne','questionnaire','2026-08-29 16:49:57'),(79,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788022293/skinora/uploads/hb7v02prfseoppighng5.jpg','Dry',0.8515,'Acne',0.8923,'Dry_Acne','direct','2026-08-29 16:51:34'),(80,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788022334/skinora/uploads/t57hllbslm0sxbnahojf.jpg','Dry',0.6361,'NoAcne',0.985,'Dry_NoAcne','questionnaire','2026-08-29 16:52:16'),(81,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788022408/skinora/uploads/slqsd0mofl8wj57gnvb0.jpg','Normal',0.8973,'NoAcne',1,'Normal_NoAcne','direct','2026-08-29 16:53:30'),(82,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788022446/skinora/uploads/cxibmg5zdktnwiqlzq4t.jpg','Normal',0.9802,'Acne',0.9733,'Normal_Acne','direct','2026-08-29 16:54:08'),(83,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788022474/skinora/uploads/pwkgwc8frrtjfaqzoaji.jpg','Normal',0.8379,'NoAcne',0.794,'Normal_NoAcne','direct','2026-08-29 16:54:36'),(84,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1788024890/skinora/uploads/qm1uwnr7hrzavez4bcyt.jpg','Normal',0.905,'Acne',0.9436,'Normal_Acne','direct','2026-08-29 17:34:52'),(85,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1788024976/skinora/uploads/whvpiyrfapprxbuigkvr.jpg','Normal',0.905,'Acne',0.9436,'Normal_Acne','direct','2026-08-29 17:36:17'),(86,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1788025035/skinora/uploads/wusxskjyo51z2wbz6dkw.jpg','Dry',0.6589,'Acne',0.9966,'Dry_Acne','direct','2026-08-29 17:37:17'),(87,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1788025106/skinora/uploads/mmc1hgednszjmkia445j.jpg','Oily',0.5693,'Acne',0.7717,'Oily_Acne','questionnaire','2026-08-29 17:38:27'),(88,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1788025134/skinora/uploads/mjzcdrl9uqwrkptcpkmy.jpg','Dry',0.5261,'Acne',0.999,'Dry_Acne','questionnaire','2026-08-29 17:38:56'),(89,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1788025160/skinora/uploads/pnyytmsq4sjofptvpsfu.jpg','Dry',0.5882,'Acne',1,'Dry_Acne','questionnaire','2026-08-29 17:39:22'),(90,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1788025197/skinora/uploads/hkhqnkjp84fhrrpedia4.jpg','Oily',0.5196,'Acne',1,'Oily_Acne','questionnaire','2026-08-29 17:39:59'),(91,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1788025267/skinora/uploads/iaz7royayaf3hxldhave.jpg','Normal',0.7701,'Acne',0.9999,'Normal_Acne','direct','2026-08-29 17:41:08'),(92,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788025374/skinora/uploads/f8ituqscfw2rzfdzr4j5.jpg','Normal',0.7701,'Acne',0.9999,'Normal_Acne','direct','2026-08-29 17:42:55'),(93,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1788026291/skinora/uploads/gyvnjvkivzdhmn0xshfz.jpg','Normal',0.8035,'NoAcne',0.992,'Normal_NoAcne','direct','2026-08-29 17:58:13'),(94,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1788026396/skinora/uploads/s2uzn54kjlyqrhoeieht.jpg','Oily',0.5196,'Acne',1,'Oily_Acne','questionnaire','2026-08-29 17:59:57'),(95,10,'https://res.cloudinary.com/wihktw8b/image/upload/v1788066567/skinora/uploads/z0v6svyed4zyvcohyfdm.jpg','Normal',0.7997,'NoAcne',0.5071,'Normal_NoAcne','questionnaire','2026-08-30 05:09:29'),(96,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788074905/skinora/uploads/czn5wi9eu8f26st1e42u.jpg','Normal',0.8973,'NoAcne',1,'Normal_NoAcne','direct','2026-08-30 07:28:27'),(97,14,'https://res.cloudinary.com/wihktw8b/image/upload/v1788074976/skinora/uploads/xvwgtf2otc7zainl2hfz.jpg','Dry',0.6589,'Acne',0.9966,'Dry_Acne','direct','2026-08-30 07:29:37');
/*!40000 ALTER TABLE `detections` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `email_otps`
--

DROP TABLE IF EXISTS `email_otps`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `email_otps` (
  `id` int NOT NULL AUTO_INCREMENT,
  `email` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `otp_code` varchar(6) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime DEFAULT NULL,
  `expires_at` datetime NOT NULL,
  `verified_at` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_email_otps_email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `email_otps`
--

LOCK TABLES `email_otps` WRITE;
/*!40000 ALTER TABLE `email_otps` DISABLE KEYS */;
INSERT INTO `email_otps` VALUES (2,'abx@gmail.com','980941','2026-08-22 13:45:18','2026-08-22 13:55:18',NULL),(3,'yourname@gmail.com','881926','2026-08-28 05:48:41','2026-08-28 05:58:41',NULL),(6,'chamaribandara77@gmail.com','174804','2026-08-29 18:27:11','2026-08-29 18:37:11',NULL);
/*!40000 ALTER TABLE `email_otps` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questionnaire_responses`
--

DROP TABLE IF EXISTS `questionnaire_responses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `questionnaire_responses` (
  `id` int NOT NULL AUTO_INCREMENT,
  `detection_id` int NOT NULL,
  `question_id` int NOT NULL,
  `answer_value` text NOT NULL,
  `answered_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `idx_qr_detection` (`detection_id`),
  KEY `fk_qr_question` (`question_id`),
  CONSTRAINT `fk_qr_detection` FOREIGN KEY (`detection_id`) REFERENCES `detections` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_qr_question` FOREIGN KEY (`question_id`) REFERENCES `questions` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=65 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questionnaire_responses`
--

LOCK TABLES `questionnaire_responses` WRITE;
/*!40000 ALTER TABLE `questionnaire_responses` DISABLE KEYS */;
INSERT INTO `questionnaire_responses` VALUES (25,42,1,'Less than 4 glasses','2026-08-20 14:58:34'),(26,42,2,'Medium','2026-08-20 14:58:34'),(27,42,3,'6–8 hours','2026-08-20 14:58:34'),(28,42,5,'Yes','2026-08-20 14:58:34'),(29,48,1,'More than 8 glasses','2026-08-23 14:04:10'),(30,48,2,'Medium','2026-08-23 14:04:10'),(31,48,3,'6–8 hours','2026-08-23 14:04:10'),(32,48,5,'Yes','2026-08-23 14:04:10'),(33,50,1,'More than 8 glasses','2026-08-25 14:02:56'),(34,50,2,'High','2026-08-25 14:02:56'),(35,50,3,'More than 8 hours','2026-08-25 14:02:56'),(36,50,5,'No','2026-08-25 14:02:56'),(37,50,1,'Less than 4 glasses','2026-08-25 14:03:38'),(38,50,2,'Low','2026-08-25 14:03:38'),(39,50,3,'Less than 6 hours','2026-08-25 14:03:38'),(40,50,5,'Yes','2026-08-25 14:03:38'),(41,53,1,'Less than 4 glasses','2026-08-25 15:16:33'),(42,53,2,'Low','2026-08-25 15:16:33'),(43,53,3,'Less than 6 hours','2026-08-25 15:16:33'),(44,53,5,'Yes','2026-08-25 15:16:33'),(45,57,1,'Less than 4 glasses','2026-08-26 07:50:04'),(46,57,2,'Low','2026-08-26 07:50:04'),(47,57,3,'Less than 6 hours','2026-08-26 07:50:04'),(48,57,5,'Yes','2026-08-26 07:50:04'),(49,63,1,'Less than 4 glasses','2026-08-28 13:23:32'),(50,63,2,'Low','2026-08-28 13:23:32'),(51,63,3,'Less than 6 hours','2026-08-28 13:23:32'),(52,63,5,'Yes','2026-08-28 13:23:32'),(53,67,1,'Less than 4 glasses','2026-08-28 17:44:16'),(54,67,2,'Medium','2026-08-28 17:44:16'),(55,67,3,'Less than 6 hours','2026-08-28 17:44:16'),(56,67,5,'Yes','2026-08-28 17:44:16'),(57,83,1,'Less than 4 glasses','2026-08-29 16:57:08'),(58,83,2,'Low','2026-08-29 16:57:08'),(59,83,3,'Less than 6 hours','2026-08-29 16:57:08'),(60,83,5,'Yes','2026-08-29 16:57:08'),(61,96,1,'4–8 glasses','2026-08-30 07:28:47'),(62,96,2,'Medium','2026-08-30 07:28:47'),(63,96,3,'6–8 hours','2026-08-30 07:28:47'),(64,96,5,'No','2026-08-30 07:28:47');
/*!40000 ALTER TABLE `questionnaire_responses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `questions`
--

DROP TABLE IF EXISTS `questions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `questions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `question_text` text NOT NULL,
  `category` varchar(100) NOT NULL,
  `relevance` json DEFAULT NULL,
  `answer_type` enum('yes_no','scale_1_5','multiple_choice') NOT NULL,
  `answer_options` json DEFAULT NULL,
  `sort_order` int NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=9 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `questions`
--

LOCK TABLES `questions` WRITE;
/*!40000 ALTER TABLE `questions` DISABLE KEYS */;
INSERT INTO `questions` VALUES (1,'How many glasses of water do you drink daily?','water',NULL,'multiple_choice','[\"Less than 4 glasses\", \"4–8 glasses\", \"More than 8 glasses\"]',1),(2,'How would you rate your stress level?','stress',NULL,'multiple_choice','[\"Low\", \"Medium\", \"High\"]',2),(3,'How many hours of sleep do you get per night?','sleep',NULL,'multiple_choice','[\"Less than 6 hours\", \"6–8 hours\", \"More than 8 hours\"]',3),(4,'Do you currently use any skincare products?','products',NULL,'yes_no','[\"yes\", \"no\"]',4),(5,'Do you consume dairy products regularly?','dairy','[\"Dry_Acne\", \"Oily_Acne\", \"Normal_Acne\"]','yes_no','[\"yes\", \"no\"]',5),(6,'How oily does your skin feel by midday?','oil_production','[\"Oily_Acne\", \"Oily_NoAcne\"]','scale_1_5',NULL,6),(7,'How often does your skin feel tight or flaky?','skin_dryness','[\"Dry_Acne\", \"Dry_NoAcne\"]','scale_1_5',NULL,7),(8,'Do you spend many hours in air-conditioned spaces?','ac_exposure','[\"Dry_Acne\", \"Dry_NoAcne\", \"Normal_NoAcne\"]','yes_no','[\"yes\", \"no\"]',8);
/*!40000 ALTER TABLE `questions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `remedies`
--

DROP TABLE IF EXISTS `remedies`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `remedies` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `ingredients` json DEFAULT NULL,
  `instructions` json NOT NULL,
  `confidence_level` enum('High','Medium') NOT NULL DEFAULT 'High',
  `source_url` text,
  `lifestyle_tags` json DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `remedies`
--

LOCK TABLES `remedies` WRITE;
/*!40000 ALTER TABLE `remedies` DISABLE KEYS */;
INSERT INTO `remedies` VALUES (1,'Aloe Vera Gel','[\"Pure aloe vera gel\"]','[\"Wash the face gently with a mild cleanser.\", \"Apply a thin, even layer of pure aloe vera gel to the entire face.\", \"Leave it on overnight.\", \"Wash off with cool water the next morning.\"]','High','https://www.nccih.nih.gov/health/aloe-vera','[\"high_stress\", \"low_water\"]'),(2,'Raw Honey Face Mask','[\"Raw honey (unpasteurised)\"]','[\"Cleanse the face with warm water.\", \"Apply a thin layer of raw honey to the face.\", \"Leave it on for 15 minutes.\", \"Rinse thoroughly with lukewarm water and pat dry.\"]','High','https://www.healthline.com/health/honey-for-face','[\"poor_sleep\"]'),(3,'Oatmeal Face Mask','[\"Plain oatmeal (finely ground)\", \"Warm water\"]','[\"Mix finely ground oatmeal with enough warm water to form a smooth paste.\", \"Apply the paste gently to the face, avoiding the eye area.\", \"Leave it on for 15 minutes.\", \"Rinse gently with cool water and pat dry.\"]','High','https://www.byrdie.com/oatmeal-facial-masks-2442870','[\"high_stress\", \"poor_sleep\"]'),(4,'Green Tea Toner','[\"Green tea bag or 1 tsp loose green tea\", \"Hot water\", \"Cotton pads\"]','[\"Brew a strong cup of green tea with hot water.\", \"Allow the tea to cool completely to room temperature.\", \"Pour into a clean bottle or bowl.\", \"Apply to the face using a cotton pad.\", \"Use once daily, preferably in the morning or evening routine.\"]','High','https://www.healthline.com/health/benefits-of-green-tea-for-skin','[\"high_stress\", \"dairy\"]'),(5,'Avocado Face Mask','[\"Half a ripe avocado\"]','[\"Mash half a ripe avocado in a bowl until smooth.\", \"Apply the mashed avocado evenly to a cleansed face.\", \"Leave it on for 15 minutes.\", \"Rinse gently with lukewarm water and pat dry.\"]','High','https://www.siobeauty.com/blogs/resource-center/6-avocado-face-mask-recipes-you-can-make-at-home','[\"low_water\", \"poor_sleep\"]'),(6,'Rose Water Toner','[\"Pure rose water\", \"Cotton pads\"]','[\"Pour pure rose water onto a clean cotton pad.\", \"Gently wipe the cotton pad across the face.\", \"Use morning and evening after cleansing.\", \"No rinsing required — allow it to absorb into the skin.\"]','High','https://plumgoodness.com/blogs/skincare/bulgarian-valley-rose-water-toner-isn-t-your-ordinary-toner','[\"high_stress\"]'),(7,'Cucumber Face Mask','[\"Half a fresh cucumber\"]','[\"Blend half a fresh cucumber until smooth.\", \"Apply the cucumber paste evenly to a cleansed face.\", \"Leave it on for 15 minutes.\", \"Rinse with cool water and pat dry.\"]','High','https://www.healthline.com/health/beauty-skin-care/cucumber-face-mask','[\"high_stress\", \"low_water\"]'),(8,'Plain Yogurt Face Mask','[\"Plain unsweetened yogurt\"]','[\"Apply a thin layer of plain unsweetened yogurt to clean skin, avoiding the eye area.\", \"Leave it on for 10–15 minutes.\", \"Rinse gently with lukewarm water.\", \"Pat the skin dry with a clean towel.\", \"Apply a gentle fragrance-free moisturizer if the skin feels dry.\"]','High','https://www.healthline.com/health/beauty-skin-care/yogurt-face-mask','[\"normal_skin\", \"dry_skin\", \"skin_soothing\"]'),(9,'Colloidal Oatmeal Moisture Mask','[\"Colloidal oatmeal (finely ground)\", \"Lukewarm water\"]','[\"Mix the finely ground colloidal oatmeal with enough lukewarm water to form a smooth paste.\", \"Apply the paste gently to clean skin, avoiding the eye area.\", \"Leave it on for 10–15 minutes.\", \"Rinse gently with lukewarm water and pat the skin dry.\", \"Apply a fragrance-free moisturizer while the skin is slightly damp.\"]','High','https://www.byrdie.com/oatmeal-facial-masks-2442870','[\"dry_skin\", \"skin_soothing\", \"low_water\"]'),(10,'Jojoba Oil Moisturizer','[\"Pure jojoba oil\"]','[\"Cleanse the face gently with a mild cleanser.\", \"Pat the face dry but leave the skin slightly damp.\", \"Place 2–3 drops of pure jojoba oil onto clean fingertips.\", \"Gently spread a thin layer over the face, avoiding the eye area.\", \"Leave it on as a moisturizing treatment.\"]','High','https://www.byrdie.com/jojoba-oil-for-skin-4783234','[\"dry_skin\", \"moisturizing\", \"low_water\"]'),(11,'Shea Butter Moisture Treatment','[\"Fragrance-free shea butter\"]','[\"Cleanse the face gently with a mild cleanser.\", \"Pat the skin dry while leaving it slightly damp.\", \"Take a very small amount of fragrance-free shea butter.\", \"Warm the shea butter between clean fingertips.\", \"Apply a thin layer to areas that feel dry, avoiding areas that are prone to clogged pores.\", \"Leave it on as a moisturizing treatment.\"]','High','https://karethic.com/en/Shea-butter--a-natural-skincare-product--is-scientifically-proven./','[\"dry_skin\", \"moisturizing\", \"acne_sensitive\"]'),(12,'Colloidal Oatmeal and Jojoba Moisture Treatment','[\"Colloidal oatmeal (finely ground)\", \"Lukewarm water\", \"Pure jojoba oil\"]','[\"Mix the colloidal oatmeal with lukewarm water to form a smooth paste.\", \"Add 2–3 drops of pure jojoba oil and mix gently.\", \"Apply a thin layer to clean skin, avoiding the eye area.\", \"Leave it on for 10–15 minutes.\", \"Rinse gently with lukewarm water.\", \"Pat the skin dry and apply a lightweight, non-comedogenic moisturizer.\"]','High','https://www.newdirectionsaromatics.com/blog/colloidal-oatmeal-a-wonder-ingredient-for-skin','[\"dry_skin\", \"acne_sensitive\", \"moisturizing\"]'),(13,'Kaolin Clay Face Mask','[\"Kaolin clay\", \"Clean water\"]','[\"Place a small amount of kaolin clay into a clean bowl.\", \"Add enough clean water to form a smooth paste.\", \"Apply a thin layer to clean skin, avoiding the eye and lip areas.\", \"Leave the mask on for approximately 5–10 minutes and do not allow it to become completely dry and cracked.\", \"Rinse gently with lukewarm water.\", \"Pat the skin dry and apply a lightweight, non-comedogenic moisturizer.\"]','High','https://skinkraft.com/blogs/articles/kaolin-clay-for-skin','[\"oily_skin\", \"acne_prone\", \"excess_oil\"]'),(14,'Diluted Tea Tree Oil Spot Treatment','[\"Tea tree essential oil\", \"Jojoba oil\"]','[\"Mix a small amount of tea tree essential oil with jojoba oil to create a properly diluted mixture.\", \"Perform a patch test on a small area of skin before facial use.\", \"Apply a very small amount only to individual acne-prone spots using a clean cotton swab.\", \"Avoid the eyes, lips, and broken skin.\", \"Leave the treatment on the skin and stop using it if burning, redness, or significant irritation occurs.\"]','High','https://www.aroma-zone.com/en/page/how-to-use-tea-tree-to-eliminate-pimples-aroma-zone','[\"oily_skin\", \"acne_prone\", \"spot_treatment\"]'),(15,'Kaolin Clay Balancing Mask','[\"Kaolin clay\", \"Clean water\"]','[\"Mix kaolin clay with enough clean water to form a smooth paste.\", \"Apply a thin layer to the oily areas of the face.\", \"Leave it on for 5–10 minutes without allowing the mask to become completely dry and cracked.\", \"Rinse gently with lukewarm water.\", \"Pat the skin dry.\", \"Apply a lightweight moisturizer if the skin feels dry.\"]','High','https://www.asianbeautyx.com/blogs/the-moxie/here-s-what-you-need-to-know-before-choosing-your-next-clay-mask?srsltid=AfmBOoqjTcyqUfMoB_oC5JLQ3vwJp6ON4gpbVOG__tOM8aYOFMl2AGWA','[\"oily_skin\", \"oil_control\", \"skin_balance\"]'),(16,'Jojoba Oil Light Moisturizer','[\"Pure jojoba oil\"]','[\"Cleanse the face gently with a mild cleanser.\", \"Pat the skin dry while leaving it slightly damp.\", \"Apply 1–2 drops of jojoba oil to clean fingertips.\", \"Spread a very thin layer over areas that feel dry.\", \"Avoid applying a thick layer to areas that are already very oily.\"]','High','https://www.healthline.com/health/beauty-skin-care/jojoba-oil-for-face','[\"oily_skin\", \"light_moisturizing\", \"skin_balance\"]'),(17,'Shea Butter Moisture Treatment','[\"Fragrance-free shea butter\"]','[\"Cleanse the face gently with a mild cleanser.\", \"Pat the skin dry while leaving it slightly damp.\", \"Take a small amount of fragrance-free shea butter.\", \"Warm it between clean fingertips.\", \"Apply a thin layer evenly over the face.\", \"Leave it on as a moisturizing treatment.\"]','High','https://www.healthline.com/health/beauty-skin-care/what-is-shea-butter','[\"normal_skin\", \"moisturizing\", \"skin_maintenance\"]'),(18,'Jojoba Oil Hydrating Treatment','[\"Pure jojoba oil\"]','[\"Wash the face gently with a mild cleanser.\", \"Pat the skin dry while leaving it slightly damp.\", \"Apply 2–3 drops of jojoba oil to clean fingertips.\", \"Massage the oil gently over the face using light circular movements.\", \"Avoid the eye area.\", \"Leave it on as a lightweight moisturizing treatment.\"]','High','https://www.healthline.com/health/beauty-skin-care/jojoba-oil-for-face','[\"normal_skin\", \"hydration\", \"moisturizing\"]'),(19,'Chamomile Compress','[\"Chamomile tea bag\", \"Clean water\"]','[\"Steep one chamomile tea bag in clean hot water for several minutes.\", \"Allow the tea to cool completely to a comfortable temperature.\", \"Soak a clean soft cloth in the cooled tea.\", \"Gently place the damp cloth on the face for 5–10 minutes.\", \"Remove the cloth and allow the skin to dry naturally.\", \"Apply a gentle, non-comedogenic moisturizer if needed.\"]','High','https://www.healthline.com/health/chamomile-oil','[\"normal_skin\", \"skin_soothing\", \"acne_sensitive\"]'),(20,'Diluted Tea Tree Oil Treatment','[\"Tea tree essential oil\", \"Jojoba oil\"]','[\"Mix the tea tree essential oil with jojoba oil to create a properly diluted mixture.\", \"Patch test the diluted mixture on a small area before applying it to the face.\", \"Apply a small amount only to acne-prone spots using a clean cotton swab.\", \"Avoid the eyes, lips, and broken skin.\", \"Leave it on the skin and discontinue use if burning, redness, itching, or irritation develops.\"]','High','https://www.healthline.com/nutrition/tea-tree-oil','[\"normal_skin\", \"acne_prone\", \"spot_treatment\"]');
/*!40000 ALTER TABLE `remedies` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tracking`
--

DROP TABLE IF EXISTS `tracking`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tracking` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `detection_id` int DEFAULT NULL,
  `remedy_id` int NOT NULL,
  `frequency` enum('weekly','monthly') NOT NULL DEFAULT 'weekly',
  `next_reminder` datetime DEFAULT NULL,
  `last_status` enum('better','no_progress','worse') DEFAULT NULL,
  `is_active` tinyint(1) NOT NULL DEFAULT '1',
  `started_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `reminders_paused` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `idx_tracking_user` (`user_id`),
  KEY `idx_tracking_next` (`next_reminder`),
  KEY `fk_tracking_detection` (`detection_id`),
  KEY `fk_tracking_remedy` (`remedy_id`),
  CONSTRAINT `fk_tracking_detection` FOREIGN KEY (`detection_id`) REFERENCES `detections` (`id`) ON DELETE SET NULL,
  CONSTRAINT `fk_tracking_remedy` FOREIGN KEY (`remedy_id`) REFERENCES `remedies` (`id`) ON DELETE RESTRICT,
  CONSTRAINT `fk_tracking_user` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tracking`
--

LOCK TABLES `tracking` WRITE;
/*!40000 ALTER TABLE `tracking` DISABLE KEYS */;
INSERT INTO `tracking` VALUES (1,2,1,5,'weekly','2026-09-06 17:55:51',NULL,1,'2026-07-05 12:24:13',0),(14,2,35,3,'weekly','2026-09-06 19:55:53','no_progress',1,'2026-08-16 12:39:03',0),(15,10,40,5,'weekly','2026-08-30 21:00:30','worse',1,'2026-08-16 13:20:54',0),(16,10,42,1,'weekly','2026-09-04 09:11:16',NULL,1,'2026-08-20 14:59:37',0),(17,10,43,2,'weekly','2026-09-05 22:13:08','no_progress',1,'2026-08-22 16:22:43',0),(18,10,45,1,'weekly','2026-09-05 23:13:07','no_progress',1,'2026-08-22 16:37:30',0),(19,10,50,4,'weekly','2026-09-01 20:02:37',NULL,1,'2026-08-25 14:32:37',0),(20,10,50,4,'weekly','2026-09-01 20:27:55','no_progress',1,'2026-08-25 14:36:57',0),(21,10,53,2,'weekly','2026-09-01 20:47:58','better',1,'2026-08-25 15:16:43',0),(22,10,57,2,'weekly','2026-09-04 18:35:06','no_progress',1,'2026-08-26 07:50:59',0),(24,10,63,9,'weekly','2026-09-04 18:55:21','better',1,'2026-08-28 13:23:52',0),(25,10,67,2,'weekly','2026-09-05 23:11:08','better',1,'2026-08-28 17:49:21',0),(26,14,83,12,'monthly','2026-09-28 23:12:55','worse',1,'2026-08-29 17:42:23',0),(27,14,96,1,'weekly','2026-09-06 12:59:37','worse',1,'2026-08-30 07:28:55',0);
/*!40000 ALTER TABLE `tracking` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `users`
--

DROP TABLE IF EXISTS `users`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `users` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password_hash` varchar(255) DEFAULT NULL,
  `google_id` varchar(255) DEFAULT NULL,
  `avatar_url` text,
  `is_verified` tinyint(1) NOT NULL DEFAULT '0',
  `verification_token` varchar(255) DEFAULT NULL,
  `created_at` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_users_email` (`email`),
  UNIQUE KEY `uq_users_google` (`google_id`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `users`
--

LOCK TABLES `users` WRITE;
/*!40000 ALTER TABLE `users` DISABLE KEYS */;
INSERT INTO `users` VALUES (2,'Osanda Gunatilake','osandagunathilake300@gmail.com',NULL,'115571640617886582439','https://lh3.googleusercontent.com/a/ACg8ocL3dY-dtWS_Cq03tM3lYPV_piLtanP_yewfbt4dkICMdFLEEw=s96-c',1,NULL,'2026-07-05 03:58:19'),(10,'Sanu Laptop','sanulaptop10@gmail.com',NULL,'103207127594868429960','https://lh3.googleusercontent.com/a/ACg8ocJ4fwFk5uZ33nOzj5S7dSVGYPkLibPlc1w0H3uTvcebR42Peg=s96-c',1,NULL,'2026-08-16 13:18:39'),(11,'abc','abc@gmail.com','$2b$12$Ggk8wZmbfZE/oN9tb69lUuOQXUGrO9C4dJzC8Qu98toqeNUSUAh0i',NULL,NULL,1,NULL,'2026-08-16 14:53:10'),(12,'medis','mendisshwn@gmail.com','$2b$12$u99Xd6pvT20mN6fPe9ocQeQmr24R40lqvvTPUUappnsFISfa/oHlu',NULL,NULL,1,NULL,'2026-08-22 13:41:55'),(14,'Gaurangana','gausajali@gmail.com','$2b$12$zAjbXXYwy8dASXOxUJUk9uKbS/ZlI4BWTNLq/aHfMMgQ6NyVRCnFq','118051593517802105100','https://lh3.googleusercontent.com/a/ACg8ocIXgNjf11BSwK5HdPPWYGh_z6Ebhx29plhVyQTKbooRv-hbqg=s96-c',1,NULL,'2026-08-29 16:09:54');
/*!40000 ALTER TABLE `users` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-08-30 22:09:18
