-- phpMyAdmin SQL Dump
-- version 4.4.7
-- http://www.phpmyadmin.net
--
-- VÃ¤rd: localhost:3306
-- Tid vid skapande: 10 aug 2015 kl 06:37
-- Serverversion: 5.6.25
-- PHP-version: 5.5.27

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- Databas: `speedtest`
--

--
-- Dumpning av Data i tabell `request`
--

INSERT INTO `request` (`rqid`, `rqmac`, `rqdeviceid`, `rqserviceorderid`, `rqrspid`, `rqstatus`, `rqbwdown`, `rqbwup`, `rqtimestamp`, `rqcreated`) VALUES(1, '00:0c:29:59:59:7b', 1, 200074, 1, 1, '10', '1', '2015-08-10 12:04:06', '2015-08-11 00:04:06');

--
-- Dumpning av Data i tabell `request_history`
--

INSERT INTO `request_history` (`rqhid`, `rqhrqid`, `rqhlog`, `rqhtime`) VALUES(1, 1, 'Created request', '2015-08-10 12:14:41');

--
-- Dumpning av Data i tabell `request_status`
--

INSERT INTO `request_status` (`rqsid`, `rqsname`) VALUES(1, 'New');
INSERT INTO `request_status` (`rqsid`, `rqsname`) VALUES(2, 'In Progress');
INSERT INTO `request_status` (`rqsid`, `rqsname`) VALUES(3, 'Completed');
INSERT INTO `request_status` (`rqsid`, `rqsname`) VALUES(4, 'Timed Out');
INSERT INTO `request_status` (`rqsid`, `rqsname`) VALUES(5, 'Error');
INSERT INTO `request_status` (`rqsid`, `rqsname`) VALUES(6, 'Overridden');

--
-- Dumpning av Data i tabell `rsp`
--

INSERT INTO `rsp` (`rspid`, `rspname`) VALUES(1, 'Spark');
INSERT INTO `rsp` (`rspid`, `rspname`) VALUES(2, 'Vodafone');
INSERT INTO `rsp` (`rspid`, `rspname`) VALUES(3, 'CallPlus');

--
-- Dumpning av Data i tabell `rsp_serverlist`
--

INSERT INTO `rsp_serverlist` (`rspslrspid`, `rspslsrvid`) VALUES(1, 4118);
INSERT INTO `rsp_serverlist` (`rspslrspid`, `rspslsrvid`) VALUES(1, 4135);
INSERT INTO `rsp_serverlist` (`rspslrspid`, `rspslsrvid`) VALUES(1, 4136);
INSERT INTO `rsp_serverlist` (`rspslrspid`, `rspslsrvid`) VALUES(2, 4934);
INSERT INTO `rsp_serverlist` (`rspslrspid`, `rspslsrvid`) VALUES(2, 4953);
INSERT INTO `rsp_serverlist` (`rspslrspid`, `rspslsrvid`) VALUES(2, 4954);
INSERT INTO `rsp_serverlist` (`rspslrspid`, `rspslsrvid`) VALUES(3, 2757);
INSERT INTO `rsp_serverlist` (`rspslrspid`, `rspslsrvid`) VALUES(3, 5749);

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
