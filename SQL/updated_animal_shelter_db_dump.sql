DROP TABLE IF EXISTS `Animals`;
DROP TABLE IF EXISTS `PetOwners`;
DROP TABLE IF EXISTS `AdoptionEvents`;
DROP TABLE IF EXISTS `Volunteers`;
DROP TABLE IF EXISTS `Event_Volunteers`;
DROP TABLE IF EXISTS `Event_Animals`;

CREATE TABLE `PetOwners` (
  `pet_owner_id` INT(11) NOT NULL AUTO_INCREMENT,
  `first_name` varchar(255) NOT NULL,
  `last_name` varchar(255) NOT NULL,
  PRIMARY KEY(`pet_owner_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `Animals` (
  `animal_id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `type` varchar(255) NOT NULL,
  `pet_owner` INT(11),
  CONSTRAINT `animals_fk_owners`
    FOREIGN KEY (`pet_owner`)
    REFERENCES `PetOwners` (`pet_owner_id`)
    ON DELETE SET NULL
    ON UPDATE SET NULL,
  CHECK (`type` in ('dog', 'cat')),
  PRIMARY KEY(`animal_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `AdoptionEvents` (
  `event_id` INT(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `date` date NOT NULL,
  PRIMARY KEY(`event_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `Volunteers` (
  `volunteer_id` INT(11) NOT NULL AUTO_INCREMENT,
  `first_name` varchar(255) NOT NULL,
  `last_name` varchar(255) NOT NULL,
  PRIMARY KEY(`volunteer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `Event_Volunteers` (
  `event_id` INT(11),
  `volunteer_id` INT(11),
  CONSTRAINT `event_volunteers_fk_events`
    FOREIGN KEY (`event_id`)
    REFERENCES `AdoptionEvents` (`event_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `event_volunteers_fk_volunteers`
    FOREIGN KEY (`volunteer_id`)
    REFERENCES `Volunteers` (`volunteer_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  PRIMARY KEY(`event_id`, `volunteer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

CREATE TABLE `Event_Animals` (
  `event_id` INT(11),
  `animal_id` INT(11),
  CONSTRAINT `event_animals_fk_events`
    FOREIGN KEY (`event_id`)
    REFERENCES `AdoptionEvents` (`event_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `event_animals_fk_animals`
    FOREIGN KEY (`animal_id`)
    REFERENCES `Animals` (`animal_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  PRIMARY KEY(`event_id`, `animal_id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;

INSERT INTO Animals (name, type)
  VALUES
    ('Baxter', 'dog'),
    ('Cooper', 'cat'),
    ('Leo', 'cat');

INSERT INTO PetOwners (first_name, last_name)
  VALUES
    ('Benny', 'Smith'),
    ('Steve', 'Doe'),
    ('Jessica', 'Harper');

INSERT INTO Animals (name, type, pet_owner)
  VALUES
    ('Boxer', 'dog',
      (SELECT pet_owner_id FROM PetOwners WHERE first_name = 'Benny' AND last_name = 'Smith')),
    ('Princess', 'dog',
      (SELECT pet_owner_id FROM PetOwners WHERE first_name = 'Steve' AND last_name = 'Doe')),
    ('Anna', 'cat',
      (SELECT pet_owner_id FROM PetOwners WHERE first_name = 'Jessica' AND last_name = 'Harper')),
    ('Elsa', 'cat',
      (SELECT pet_owner_id FROM PetOwners WHERE first_name = 'Jessica' AND last_name = 'Harper'));

INSERT INTO AdoptionEvents (name, date)
  VALUES
    ('Pet Valentine Adoption Event', '2020/02/14'),
    ('First Lutheran Church Adoption Event', '2020/03/14'),
    ('Riverside Park Adoption Event', '2020/04/14');

INSERT INTO Volunteers (first_name, last_name)
  VALUES
    ('Stephen', 'Curry'),
    ('Lebron', 'James'),
    ('Angelina', 'Jolie');

INSERT INTO Event_Volunteers (event_id, volunteer_id)
  VALUES
    ((SELECT event_id FROM AdoptionEvents WHERE name = 'Pet Valentine Adoption Event'),
     (SELECT volunteer_id FROM Volunteers WHERE first_name = 'Angelina' and last_name = 'Jolie')),
    ((SELECT event_id FROM AdoptionEvents WHERE name = 'First Lutheran Church Adoption Event'),
     (SELECT volunteer_id FROM Volunteers WHERE first_name = 'Lebron' and last_name = 'James')),
    ((SELECT event_id FROM AdoptionEvents WHERE name = 'Riverside Park Adoption Event'),
     (SELECT volunteer_id FROM Volunteers WHERE first_name = 'Stephen' and last_name = 'Curry'));


INSERT INTO Event_Animals (event_id, animal_id)
  VALUES
    ((SELECT event_id FROM AdoptionEvents WHERE name = 'Pet Valentine Adoption Event'),
     (SELECT animal_id FROM Animals WHERE name = 'Baxter')),
    ((SELECT event_id FROM AdoptionEvents WHERE name = 'Pet Valentine Adoption Event'),
    (SELECT animal_id FROM Animals WHERE name = 'Cooper')),
    ((SELECT event_id FROM AdoptionEvents WHERE name = 'Pet Valentine Adoption Event'),
    (SELECT animal_id FROM Animals WHERE name = 'Leo')),
    ((SELECT event_id FROM AdoptionEvents WHERE name = 'First Lutheran Church Adoption Event'),
    (SELECT animal_id FROM Animals WHERE name = 'Cooper')),
    ((SELECT event_id FROM AdoptionEvents WHERE name = 'First Lutheran Church Adoption Event'),
    (SELECT animal_id FROM Animals WHERE name = 'Leo')),
    ((SELECT event_id FROM AdoptionEvents WHERE name = 'Riverside Park Adoption Event'),
    (SELECT animal_id FROM Animals WHERE name = 'Baxter')),
    ((SELECT event_id FROM AdoptionEvents WHERE name = 'Riverside Park Adoption Event'),
    (SELECT animal_id FROM Animals WHERE name = 'Leo'));


--SELECT * FROM `Animals`;
--SELECT * FROM `PetOwners`;
--SELECT * FROM `AdoptionEvents`;
--SELECT * FROM `Volunteers`;
--SELECT * FROM `Event_Volunteers`;
--SELECT * FROM `Event_Animals`;
