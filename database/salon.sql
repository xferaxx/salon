-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Sep 10, 2024 at 09:43 PM
-- Server version: 10.4.24-MariaDB
-- PHP Version: 8.1.6

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `salon`
--

-- --------------------------------------------------------

--
-- Table structure for table `appointments`
--

CREATE TABLE `appointments` (
  `id` int(11) NOT NULL,
  `customer_id` int(11) DEFAULT NULL,
  `shop_id` int(11) DEFAULT NULL,
  `service_id` int(11) DEFAULT NULL,
  `appointment_date` datetime NOT NULL,
  `status` enum('pending','confirmed','canceled') DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `appointments`
--

INSERT INTO `appointments` (`id`, `customer_id`, `shop_id`, `service_id`, `appointment_date`, `status`) VALUES
(1, 1, 1, 1, '2024-09-10 12:00:00', 'confirmed'),
(2, 1, 1, 1, '2024-09-09 17:58:00', 'confirmed'),
(3, 1, 1, 1, '2024-09-15 22:00:00', 'confirmed'),
(4, 1, 1, 1, '2024-09-20 14:30:00', 'canceled'),
(5, 1, 2, 2, '2024-09-15 23:00:00', 'confirmed'),
(6, 5, 1, 1, '2024-09-25 12:45:00', 'confirmed'),
(7, 6, 1, 1, '2024-09-10 15:13:00', 'confirmed'),
(8, 6, 1, 1, '2024-09-11 15:15:00', 'confirmed'),
(9, 6, 1, 1, '2024-09-11 13:20:00', 'confirmed'),
(10, 6, 1, 1, '2024-09-10 13:38:00', 'confirmed'),
(11, 1, 1, 1, '2024-09-10 13:50:00', 'confirmed'),
(12, 6, 1, 1, '2024-09-10 13:55:00', 'confirmed'),
(13, 6, 1, 1, '2024-09-10 13:57:00', 'confirmed'),
(14, 6, 1, 1, '2024-09-10 14:10:00', 'confirmed'),
(15, 6, 1, 1, '2024-09-10 14:07:00', 'confirmed'),
(16, 5, 3, 3, '2024-09-11 17:00:00', 'confirmed'),
(17, 5, 4, 4, '2024-09-12 17:30:00', 'confirmed'),
(18, 5, 1, 1, '2024-09-10 18:24:00', 'confirmed'),
(19, 5, 1, 1, '2024-09-18 20:45:00', 'confirmed'),
(20, 5, 5, 5, '2024-09-25 18:30:00', 'confirmed');

-- --------------------------------------------------------

--
-- Table structure for table `services`
--

CREATE TABLE `services` (
  `id` int(11) NOT NULL,
  `shop_id` int(11) DEFAULT NULL,
  `service_name` varchar(255) NOT NULL,
  `price` decimal(10,2) NOT NULL,
  `duration` int(11) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `services`
--

INSERT INTO `services` (`id`, `shop_id`, `service_name`, `price`, `duration`) VALUES
(1, 1, 'Nails Polish', '150.00', 60),
(2, 2, 'nails fix', '150.00', 60),
(3, 3, 'hair styiling regualar', '100.00', 60),
(4, 4, 'nails fixes', '150.00', 60),
(5, 5, 'nail fixes', '150.00', 60);

-- --------------------------------------------------------

--
-- Table structure for table `shops`
--

CREATE TABLE `shops` (
  `id` int(11) NOT NULL,
  `owner_id` int(11) DEFAULT NULL,
  `name` varchar(255) NOT NULL,
  `address` varchar(255) NOT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `is_approved` tinyint(1) DEFAULT 0,
  `profile_picture` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `shops`
--

INSERT INTO `shops` (`id`, `owner_id`, `name`, `address`, `phone`, `is_approved`, `profile_picture`) VALUES
(1, 2, 'JEJE NAILS', 'israel, nazareth', '0502233113', 1, 'cat.png'),
(2, 4, 'Antonio salon', 'nof hagalil', '0502316223', 1, NULL),
(3, 7, 'Malak Stylis', 'israel, nazareth', '05023121', 1, NULL),
(4, 8, 'angy nails', 'abu sinan', '050231231', 1, NULL),
(5, 9, 'et nails', 'israel, nazareth', '050522131', 1, NULL);

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `id` int(11) NOT NULL,
  `username` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `role` enum('customer','shop_owner','admin') NOT NULL,
  `profile_picture` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`id`, `username`, `password`, `email`, `role`, `profile_picture`) VALUES
(1, 'xferax', '123456', 'xferax@gmail.com', 'customer', NULL),
(2, 'nails', 'nails', 'nails@gmail.com', 'shop_owner', NULL),
(3, 'legend', 'legend', 'legend@gmail.com', 'admin', NULL),
(4, 'antonio', '123546', 'antonio@gmail.com', 'shop_owner', NULL),
(5, 'a', 'a', 'a@gmail.com', 'customer', NULL),
(6, 'jul', 'jul', 'juliankh22@gmail.com', 'customer', NULL),
(7, 'malak', 'malak', 'malak@gmail.com', 'shop_owner', NULL),
(8, 'angy', 'angy', 'angy@hotmail.com', 'shop_owner', NULL),
(9, 'e', 'e', 'e@gmail.com', 'shop_owner', NULL),
(10, 'test', 'test', 'test@gmail.com', 'customer', NULL),
(11, 'test1', 'test1', 'test1@gmail.com', 'customer', NULL),
(12, 'test2', 'test2', 'test2@gmail.com', 'customer', 'icongit.png'),
(13, 'test3', 'test3', 'test3@gmail.com', 'customer', 'me_LE_auto_x2-fotor-2024090253658-1024x1024.png'),
(14, 's', 's', 's@gmail.com', 'customer', 'cat.png'),
(15, 'ss', 'ss', 'ss@gmail.com', 'shop_owner', 'wp.jpg'),
(16, 'sss', 'sss', 'sss@gmail.com', 'shop_owner', 'myblog.png');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `appointments`
--
ALTER TABLE `appointments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `customer_id` (`customer_id`),
  ADD KEY `shop_id` (`shop_id`),
  ADD KEY `service_id` (`service_id`);

--
-- Indexes for table `services`
--
ALTER TABLE `services`
  ADD PRIMARY KEY (`id`),
  ADD KEY `shop_id` (`shop_id`);

--
-- Indexes for table `shops`
--
ALTER TABLE `shops`
  ADD PRIMARY KEY (`id`),
  ADD KEY `owner_id` (`owner_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `appointments`
--
ALTER TABLE `appointments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `services`
--
ALTER TABLE `services`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `shops`
--
ALTER TABLE `shops`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=17;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `appointments`
--
ALTER TABLE `appointments`
  ADD CONSTRAINT `appointments_ibfk_1` FOREIGN KEY (`customer_id`) REFERENCES `users` (`id`),
  ADD CONSTRAINT `appointments_ibfk_2` FOREIGN KEY (`shop_id`) REFERENCES `shops` (`id`),
  ADD CONSTRAINT `appointments_ibfk_3` FOREIGN KEY (`service_id`) REFERENCES `services` (`id`);

--
-- Constraints for table `services`
--
ALTER TABLE `services`
  ADD CONSTRAINT `services_ibfk_1` FOREIGN KEY (`shop_id`) REFERENCES `shops` (`id`);

--
-- Constraints for table `shops`
--
ALTER TABLE `shops`
  ADD CONSTRAINT `shops_ibfk_1` FOREIGN KEY (`owner_id`) REFERENCES `users` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
