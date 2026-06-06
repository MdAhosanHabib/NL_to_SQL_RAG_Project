-- Customers
INSERT INTO customers (full_name, email, phone, address) VALUES
('Rahul Ahmed',       'rahul.ahmed@mail.com',   '01711-101010', 'Gulshan, Dhaka'),
('Fatima Khatun',     'fatima.k@mail.com',      '01811-202020', 'Dhanmondi, Dhaka'),
('Mohammad Hasan',    'mhasan@mail.com',         '01911-303030', 'Mirpur, Dhaka'),
('Priya Das',         'priya.das@mail.com',      '01712-404040', 'Uttara, Dhaka'),
('Karim Molla',       'k.molla@mail.com',        '01812-505050', 'Motijheel, Dhaka'),
('Nasrin Begum',      'nasrin.b@mail.com',       '01912-606060', 'Mohammadpur, Dhaka'),
('Tanvir Islam',      'tanvir.islam@mail.com',   '01713-707070', 'Banani, Dhaka'),
('Sumaiya Akter',     'sumaiya.a@mail.com',      '01813-808080', 'Rayer Bazar, Dhaka'),
('Arif Hossain',      'arif.h@mail.com',         '01913-909090', 'Wari, Dhaka'),
('Nusrat Jahan',      'nusrat.j@mail.com',       '01714-010101', 'Lalbagh, Dhaka');

-- Accounts (2–3 per customer)
INSERT INTO accounts (customer_id, account_number, account_type, balance, status) VALUES
(1,  'BD-SAV-001001', 'savings',  125000.00, 'active'),
(1,  'BD-CHK-001002', 'checking',  45000.00, 'active'),
(2,  'BD-SAV-002001', 'savings',  280000.00, 'active'),
(3,  'BD-CHK-003001', 'checking',  75000.00, 'active'),
(3,  'BD-LON-003002', 'loan',    -250000.00, 'active'),
(4,  'BD-SAV-004001', 'savings',  550000.00, 'active'),
(4,  'BD-CHK-004002', 'checking', 120000.00, 'active'),
(5,  'BD-SAV-005001', 'savings',   90000.00, 'active'),
(5,  'BD-LON-005002', 'loan',    -180000.00, 'active'),
(6,  'BD-CHK-006001', 'checking',  35000.00, 'active'),
(7,  'BD-SAV-007001', 'savings',  420000.00, 'active'),
(7,  'BD-CHK-007002', 'checking',  85000.00, 'active'),
(8,  'BD-SAV-008001', 'savings',   65000.00, 'frozen'),
(9,  'BD-SAV-009001', 'savings',  195000.00, 'active'),
(9,  'BD-CHK-009002', 'checking',  50000.00, 'active'),
(10, 'BD-SAV-010001', 'savings',  310000.00, 'active');

-- Transactions
INSERT INTO transactions (account_id, transaction_type, amount, description, transaction_date, balance_after) VALUES
(1,  'credit',   50000.00, 'Salary deposit',         NOW() - INTERVAL '25 days', 125000.00),
(1,  'debit',    15000.00, 'Utility bill payment',   NOW() - INTERVAL '15 days', 110000.00),
(1,  'credit',   30000.00, 'Freelance income',       NOW() - INTERVAL '5 days',  140000.00),
(2,  'debit',    20000.00, 'Shopping at Jamuna',     NOW() - INTERVAL '20 days',  25000.00),
(2,  'credit',   80000.00, 'Monthly salary',         NOW() - INTERVAL '10 days', 105000.00),
(3,  'credit',   75000.00, 'Business revenue',       NOW() - INTERVAL '30 days',  75000.00),
(3,  'debit',    18000.00, 'Rent payment',           NOW() - INTERVAL '12 days',  57000.00),
(4,  'credit',  100000.00, 'Investment return',      NOW() - INTERVAL '22 days', 550000.00),
(4,  'debit',    50000.00, 'Equipment purchase',     NOW() - INTERVAL '8 days',  500000.00),
(5,  'credit',   40000.00, 'Salary',                 NOW() - INTERVAL '28 days',  90000.00),
(5,  'debit',    12000.00, 'Grocery',                NOW() - INTERVAL '6 days',   78000.00),
(7,  'credit',  200000.00, 'Property rental income', NOW() - INTERVAL '18 days', 420000.00),
(7,  'debit',    30000.00, 'Insurance premium',      NOW() - INTERVAL '3 days',  390000.00),
(9,  'credit',   60000.00, 'Salary credit',          NOW() - INTERVAL '27 days', 195000.00),
(9,  'debit',    25000.00, 'School fees',            NOW() - INTERVAL '9 days',  170000.00),
(10, 'credit',  150000.00, 'Business profit',        NOW() - INTERVAL '14 days', 310000.00),
(10, 'debit',    40000.00, 'Tax payment',            NOW() - INTERVAL '4 days',  270000.00);

