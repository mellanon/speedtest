-- phpMyAdmin SQL Dump
-- version 4.4.7
-- http://www.phpmyadmin.net
--
-- VÃ¤rd: localhost:3306
-- Tid vid skapande: 10 aug 2015 kl 06:35
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

-- --------------------------------------------------------

--
-- Tabellstruktur `request`
--

CREATE TABLE IF NOT EXISTS `request` (
  `rqid` int(11) NOT NULL,
  `rqmac` varchar(20) NOT NULL,
  `rqdeviceid` int(11) NOT NULL,
  `rqserviceorderid` int(11) NOT NULL,
  `rqrspid` int(11) NOT NULL,
  `rqstatus` int(11) NOT NULL DEFAULT '1',
  `rqbwdown` decimal(10,0) NOT NULL,
  `rqbwup` decimal(10,0) NOT NULL,
  `rqtimestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `rqcreated` varchar(30) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Tabellstruktur `request_history`
--

CREATE TABLE IF NOT EXISTS `request_history` (
  `rqhid` int(11) NOT NULL,
  `rqhrqid` int(11) NOT NULL,
  `rqhlog` varchar(255) NOT NULL,
  `rqhtime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Tabellstruktur `request_status`
--

CREATE TABLE IF NOT EXISTS `request_status` (
  `rqsid` int(11) NOT NULL,
  `rqsname` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Tabellstruktur `result`
--

CREATE TABLE IF NOT EXISTS `result` (
  `id` int(11) NOT NULL,
  `deviceid` int(11) NOT NULL,
  `sessionid` char(16) DEFAULT NULL,
  `msg` text NOT NULL,
  `created` varchar(30) DEFAULT NULL,
  `processed` tinyint(4) NOT NULL DEFAULT '0',
  `processed_time` varchar(30) NOT NULL,
  `timestamp` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Tabellstruktur `rsp`
--

CREATE TABLE IF NOT EXISTS `rsp` (
  `rspid` int(11) NOT NULL,
  `rspname` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Tabellstruktur `rsp_serverlist`
--

CREATE TABLE IF NOT EXISTS `rsp_serverlist` (
  `rspslrspid` int(11) NOT NULL,
  `rspslsrvid` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- --------------------------------------------------------

--
-- Tabellstruktur `serverlist`
--

CREATE TABLE IF NOT EXISTS `serverlist` (
  `srvid` int(11) NOT NULL,
  `srvname` varchar(255) NOT NULL,
  `srvcountry` varchar(50) NOT NULL,
  `srvcity` varchar(255) NOT NULL,
  `srvdistance` double NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

--
-- Index fÃ¶r dumpade tabeller
--

--
-- Index fÃ¶r tabell `request`
--
ALTER TABLE `request`
  ADD PRIMARY KEY (`rqid`);

--
-- Index fÃ¶r tabell `request_history`
--
ALTER TABLE `request_history`
  ADD PRIMARY KEY (`rqhid`);

--
-- Index fÃ¶r tabell `request_status`
--
ALTER TABLE `request_status`
  ADD PRIMARY KEY (`rqsid`);

--
-- Index fÃ¶r tabell `result`
--
ALTER TABLE `result`
  ADD PRIMARY KEY (`id`);

--
-- Index fÃ¶r tabell `rsp`
--
ALTER TABLE `rsp`
  ADD PRIMARY KEY (`rspid`);

--
-- Index fÃ¶r tabell `rsp_serverlist`
--
ALTER TABLE `rsp_serverlist`
  ADD PRIMARY KEY (`rspslrspid`,`rspslsrvid`);

--
-- Index fÃ¶r tabell `serverlist`
--
ALTER TABLE `serverlist`
  ADD UNIQUE KEY `srvid` (`srvid`);

--
-- AUTO_INCREMENT fÃ¶r dumpade tabeller
--

--
-- AUTO_INCREMENT fÃ¶r tabell `request`
--
ALTER TABLE `request`
  MODIFY `rqid` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT fÃ¶r tabell `request_history`
--
ALTER TABLE `request_history`
  MODIFY `rqhid` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT fÃ¶r tabell `request_status`
--
ALTER TABLE `request_status`
  MODIFY `rqsid` int(11) NOT NULL AUTO_INCREMENT;
--
-- AUTO_INCREMENT fÃ¶r tabell `result`
--
ALTER TABLE `result`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
