# Model Comparison Results

## Question 1: List all customers whose first name is 'MARY'.

**qwen/qwen3.8-27b**
SQL:
```
SELECT * FROM customer WHERE first_name = 'MARY';
```
Result:
```
(1, 1, 'MARY', 'SMITH', 'MARY.SMITH@sakilacustomer.org', 5, 1, datetime.datetime(2006, 2, 14, 22, 4, 36), datetime.datetime(2006, 2, 15, 4, 57, 20))
```

**openai/gpt-oss-120b**
SQL:
```
SELECT * FROM customer WHERE first_name = 'MARY';
```
Result:
```
(1, 1, 'MARY', 'SMITH', 'MARY.SMITH@sakilacustomer.org', 5, 1, datetime.datetime(2006, 2, 14, 22, 4, 36), datetime.datetime(2006, 2, 15, 4, 57, 20))
```


## Question 2: Find the 5 longest films by length.

**qwen/qwen3.8-27b**
SQL:
```
SELECT title, length FROM film ORDER BY length DESC LIMIT 5;
```
Result:
```
('GANGS PRIDE', 185)
('HOME PITY', 185)
('CHICAGO NORTH', 185)
('CONTROL ANTHEM', 185)
('DARN FORRESTER', 185)
```

**openai/gpt-oss-120b**
SQL:
```
SELECT film_id, title, length
FROM film
ORDER BY length DESC
LIMIT 5;
```
Result:
```
(349, 'GANGS PRIDE', 185)
(426, 'HOME PITY', 185)
(141, 'CHICAGO NORTH', 185)
(182, 'CONTROL ANTHEM', 185)
(212, 'DARN FORRESTER', 185)
```


## Question 3: Get the titles of all films in the 'Comedy' category.

**qwen/qwen3.8-27b**
SQL:
```
SELECT f.title
FROM film f
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
WHERE c.name = 'Comedy';
```
Result:
```
('AIRPLANE SIERRA',)
('ANTHEM LUKE',)
('BRINGING HYSTERICAL',)
('CAPER MOTIONS',)
('CAT CONEHEADS',)
('CLOSER BANG',)
('CONNECTION MICROCOSMOS',)
('CONTROL ANTHEM',)
('CRAZY HOME',)
('DADDY PITTSBURGH',)
... (58 total rows)
```

**openai/gpt-oss-120b**
SQL:
```
SELECT f.title
FROM film f
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
WHERE c.name = 'Comedy';
```
Result:
```
('AIRPLANE SIERRA',)
('ANTHEM LUKE',)
('BRINGING HYSTERICAL',)
('CAPER MOTIONS',)
('CAT CONEHEADS',)
('CLOSER BANG',)
('CONNECTION MICROCOSMOS',)
('CONTROL ANTHEM',)
('CRAZY HOME',)
('DADDY PITTSBURGH',)
... (58 total rows)
```


## Question 4: Which actor has appeared in the most films?

**qwen/qwen3.8-27b**
SQL:
```
SELECT a.first_name, a.last_name
FROM actor a
JOIN film_actor fa ON a.actor_id = fa.actor_id
GROUP BY a.actor_id, a.first_name, a.last_name
ORDER BY COUNT(fa.film_id) DESC
LIMIT 1;
```
Result:
```
('GINA', 'DEGENERES')
```

**openai/gpt-oss-120b**
SQL:
```
SELECT a.actor_id, a.first_name, a.last_name, COUNT(*) AS film_count
FROM actor a
JOIN film_actor fa ON a.actor_id = fa.actor_id
GROUP BY a.actor_id, a.first_name, a.last_name
ORDER BY film_count DESC
LIMIT 1;
```
Result:
```
(107, 'GINA', 'DEGENERES', 42)
```


## Question 5: List customer names along with the film titles they've rented.

**qwen/qwen3.8-27b**
SQL:
```
SELECT c.first_name, c.last_name, f.title
FROM customer c
JOIN rental r ON c.customer_id = r.customer_id
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id;
```
Result:
```
('JOEL', 'FRANCISCO', 'ACADEMY DINOSAUR')
('GABRIEL', 'HARDER', 'ACADEMY DINOSAUR')
('DIANNE', 'SHELTON', 'ACADEMY DINOSAUR')
('NORMAN', 'CURRIER', 'ACADEMY DINOSAUR')
('BEATRICE', 'ARNOLD', 'ACADEMY DINOSAUR')
('GERALDINE', 'PERKINS', 'ACADEMY DINOSAUR')
('VIRGIL', 'WOFFORD', 'ACADEMY DINOSAUR')
('WILLIE', 'MARKHAM', 'ACADEMY DINOSAUR')
('DEBRA', 'NELSON', 'ACADEMY DINOSAUR')
('DARREN', 'WINDHAM', 'ACADEMY DINOSAUR')
... (16044 total rows)
```

**openai/gpt-oss-120b**
SQL:
```
SELECT c.first_name, c.last_name, f.title
FROM customer c
JOIN rental r ON c.customer_id = r.customer_id
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
ORDER BY c.last_name, c.first_name, f.title;
```
Result:
```
('RAFAEL', 'ABNEY', 'BLACKOUT PRIVATE')
('RAFAEL', 'ABNEY', 'CHOCOLAT HARRY')
('RAFAEL', 'ABNEY', 'CLASH FREDDY')
('RAFAEL', 'ABNEY', 'CONEHEADS SMOOCHY')
('RAFAEL', 'ABNEY', 'CONQUERER NUTS')
('RAFAEL', 'ABNEY', 'CONVERSATION DOWNHILL')
('RAFAEL', 'ABNEY', 'DOUBLE WRATH')
('RAFAEL', 'ABNEY', 'FREDDY STORM')
('RAFAEL', 'ABNEY', 'GOODFELLAS SALUTE')
('RAFAEL', 'ABNEY', 'HOBBIT ALIEN')
... (16044 total rows)
```


## Question 6: Total revenue collected by each store.

**qwen/qwen3.8-27b**
SQL:
```
SELECT s.store_id, SUM(p.amount) AS total_revenue
FROM payment p
JOIN customer c ON p.customer_id = c.customer_id
JOIN store s ON c.store_id = s.store_id
GROUP BY s.store_id;
```
Result:
```
(1, Decimal('36997.53'))
(2, Decimal('30409.03'))
```

**openai/gpt-oss-120b**
SQL:
```
SELECT s.store_id,
       SUM(p.amount) AS total_revenue
FROM payment AS p
JOIN rental   AS r ON p.rental_id = r.rental_id
JOIN inventory AS i ON r.inventory_id = i.inventory_id
JOIN store    AS s ON i.store_id = s.store_id
GROUP BY s.store_id;
```
Result:
```
(1, Decimal('33679.79'))
(2, Decimal('33726.77'))
```


## Question 7: Find customers who have never rented a film.

**qwen/qwen3.8-27b**
SQL:
```
SELECT c.customer_id, c.first_name, c.last_name
FROM customer c
LEFT JOIN rental r ON c.customer_id = r.customer_id
WHERE r.rental_id IS NULL;
```
Result:
```

```

**openai/gpt-oss-120b**
SQL:
```
SELECT c.customer_id, c.first_name, c.last_name
FROM customer c
WHERE NOT EXISTS (
    SELECT 1
    FROM rental r
    WHERE r.customer_id = c.customer_id
);
```
Result:
```

```


## Question 8: Find the top 3 most rented film categories by total rental count.

**qwen/qwen3.8-27b**
SQL:
```
SELECT c.name AS category_name, COUNT(r.rental_id) AS total_rentals
FROM film_category fc
JOIN category c ON fc.category_id = c.category_id
JOIN film f ON fc.film_id = f.film_id
JOIN inventory i ON f.film_id = i.film_id
JOIN rental r ON i.inventory_id = r.inventory_id
GROUP BY c.name
ORDER BY total_rentals DESC
LIMIT 3;
```
Result:
```
('Sports', 1179)
('Animation', 1166)
('Action', 1112)
```

**openai/gpt-oss-120b**
SQL:
```
SELECT c.name AS category, COUNT(r.rental_id) AS rental_count
FROM rental r
JOIN inventory i ON r.inventory_id = i.inventory_id
JOIN film f ON i.film_id = f.film_id
JOIN film_category fc ON f.film_id = fc.film_id
JOIN category c ON fc.category_id = c.category_id
GROUP BY c.category_id, c.name
ORDER BY rental_count DESC
LIMIT 3;
```
Result:
```
('Sports', 1179)
('Animation', 1166)
('Action', 1112)
```


## Question 9: Show me the best customers.

**qwen/qwen3.8-27b**
SQL:
```
SELECT 
    c.customer_id,
    c.first_name,
    c.last_name,
    COUNT(r.rental_id) AS total_rentals,
    SUM(p.amount) AS total_payment
FROM customer c
JOIN rental r ON c.customer_id = r.customer_id
JOIN payment p ON r.rental_id = p.rental_id
GROUP BY c.customer_id, c.first_name, c.last_name
ORDER BY total_payment DESC, total_rentals DESC
LIMIT 10;
```
Result:
```
(526, 'KARL', 'SEAL', 45, Decimal('221.55'))
(148, 'ELEANOR', 'HUNT', 46, Decimal('216.54'))
(144, 'CLARA', 'SHAW', 42, Decimal('195.58'))
(137, 'RHONDA', 'KENNEDY', 39, Decimal('194.61'))
(178, 'MARION', 'SNYDER', 39, Decimal('194.61'))
(459, 'TOMMY', 'COLLAZO', 38, Decimal('186.62'))
(469, 'WESLEY', 'BULL', 40, Decimal('177.60'))
(468, 'TIM', 'CARY', 39, Decimal('175.61'))
(236, 'MARCIA', 'DEAN', 42, Decimal('175.58'))
(181, 'ANA', 'BRADLEY', 34, Decimal('174.66'))
```

**openai/gpt-oss-120b**
SQL:
```
SELECT c.customer_id,
       c.first_name,
       c.last_name,
       SUM(p.amount) AS total_spent
FROM   customer AS c
JOIN   payment  AS p ON c.customer_id = p.customer_id
GROUP  BY c.customer_id, c.first_name, c.last_name
ORDER  BY total_spent DESC
LIMIT 10;
```
Result:
```
(526, 'KARL', 'SEAL', Decimal('221.55'))
(148, 'ELEANOR', 'HUNT', Decimal('216.54'))
(144, 'CLARA', 'SHAW', Decimal('195.58'))
(137, 'RHONDA', 'KENNEDY', Decimal('194.61'))
(178, 'MARION', 'SNYDER', Decimal('194.61'))
(459, 'TOMMY', 'COLLAZO', Decimal('186.62'))
(469, 'WESLEY', 'BULL', Decimal('177.60'))
(468, 'TIM', 'CARY', Decimal('175.61'))
(236, 'MARCIA', 'DEAN', Decimal('175.58'))
(181, 'ANA', 'BRADLEY', Decimal('174.66'))
```


## Question 10: Find categories that have more than 50 films.

**qwen/qwen3.8-27b**
SQL:
```
SELECT category.category_id, category.name
FROM category
JOIN film_category ON category.category_id = film_category.category_id
GROUP BY category.category_id, category.name
HAVING COUNT(film_category.film_id) > 50
```
Result:
```
(1, 'Action')
(2, 'Animation')
(3, 'Children')
(4, 'Classics')
(5, 'Comedy')
(6, 'Documentary')
(7, 'Drama')
(8, 'Family')
(9, 'Foreign')
(10, 'Games')
... (16 total rows)
```

**openai/gpt-oss-120b**
SQL:
```
SELECT c.name
FROM category c
JOIN film_category fc ON c.category_id = fc.category_id
GROUP BY c.category_id, c.name
HAVING COUNT(DISTINCT fc.film_id) > 50;
```
Result:
```
('Action',)
('Animation',)
('Children',)
('Classics',)
('Comedy',)
('Documentary',)
('Drama',)
('Family',)
('Foreign',)
('Games',)
... (16 total rows)
```


## Question 11: How many rentals happened in May 2005?

**qwen/qwen3.8-27b**
SQL:
```
SELECT COUNT(*) FROM rental WHERE rental_date >= '2005-05-01' AND rental_date < '2005-06-01';
```
Result:
```
(1156,)
```

**openai/gpt-oss-120b**
SQL:
```
SELECT COUNT(*) AS rentals_in_may_2005
FROM rental
WHERE rental_date >= '2005-05-01'
  AND rental_date < '2005-06-01';
```
Result:
```
(1156,)
```


## Question 12: List films that have never been rented.

**qwen/qwen3.8-27b**
SQL:
```
SELECT f.film_id, f.title
FROM film f
LEFT JOIN inventory i ON f.film_id = i.film_id
LEFT JOIN rental r ON i.inventory_id = r.inventory_id
WHERE r.rental_id IS NULL;
```
Result:
```
(1, 'ACADEMY DINOSAUR')
(14, 'ALICE FANTASIA')
(33, 'APOLLO TEEN')
(36, 'ARGONAUTS TOWN')
(38, 'ARK RIDGEMONT')
(41, 'ARSENIC INDEPENDENCE')
(87, 'BOONDOCK BALLROOM')
(108, 'BUTCH PANTHER')
(128, 'CATCH AMISTAD')
(144, 'CHINATOWN GLADIATOR')
... (43 total rows)
```

**openai/gpt-oss-120b**
SQL:
```
SELECT f.film_id, f.title
FROM film f
WHERE NOT EXISTS (
    SELECT 1
    FROM inventory i
    JOIN rental r ON i.inventory_id = r.inventory_id
    WHERE i.film_id = f.film_id
);
```
Result:
```
(14, 'ALICE FANTASIA')
(33, 'APOLLO TEEN')
(36, 'ARGONAUTS TOWN')
(38, 'ARK RIDGEMONT')
(41, 'ARSENIC INDEPENDENCE')
(87, 'BOONDOCK BALLROOM')
(108, 'BUTCH PANTHER')
(128, 'CATCH AMISTAD')
(144, 'CHINATOWN GLADIATOR')
(148, 'CHOCOLATE DUCK')
... (42 total rows)
```
