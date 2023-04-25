Nume: Dimovski Kirjan
Grupă: 332CB

# Tema 1

Organizare
-
## Marketplace
The marketplace consists of two dictionaries: `consumers` and `producers`.
`consumers` is a dictionary of lists containing all the products currently
added to the respective cart. The keys in this dictionary are the ID of every
cart. `producers` is a dictionary that counts how many products are currenty in
the queue that have been produced by each producer. The keys in this dict are
the ID of every producer. More on this at **Generating IDs**.

When a producer wants to publish a product, I check if
`producers[producer_id] < queue_size_per_producer` and if it's true, append the
product to `queue`, which is a list that contains all available products in the
marketplace, as well as incrementing `producers[producer_id]` by one. Locks are
not needed here, since `append()` is thread safe. When appending the product to
`queue`, I also append the ID of the producer. This is useful for when I add or
remove that product to a cart.

When a consumer adds a product to a cart, I search for the first instance of
that product `queue` and if its available, append it to `consumers[cart_id]`,
remove it from `queue` and decrease `producers[producer_id]`. I get
`producer_id` from `first_product[1]`, since the elements in `queue` are tuples
of a product and the producer ID. All of this is inside a `Lock()`, since
multiple consumers could try and remove the same product inside the queue.
(Thank you private checker on moodle, for telling me
`ValueError: list.remove(x): x not in list`)

Removing a product from the list follows the exact same logic, only this time
just the incrementing part of `producers[producer_id]` in in a `Lock()` since
multiple consumers may try to remove a product from their cart that belongs to
the same producer.
## Consumer
The consumer adds carts to the marketplace, which then adds or removes products
to them. If it tries to add a product which isn't available on the marketplace
it sleeps for `retry_wait_time`.
## Producer
The producer publishes products to the marketplace. If his limit has been
reached, he waits for `republish_wait_time`. If he published a product, he then
waits for `wait_time`
## Generating IDs
For generating the IDs of the Producers I opted to use the built-in `uuid`
library. This avoids using sequantial IDs and adds the benefit of not allowing
the producers to be listed, as they are initialized with random IDs. I used the
same reasoning when generating IDs for the consumers, except they are modified
to be ints and up to 999,999, which is more than enough for the homework.

The homework was very useful for getting used to Python and its'
functionalities. I love the fact that the homework was more about figuring out
the problem instead of fighting the language.


Implementare
-
The entire homework is implemented. All tests pass locally.
I had problems with test 8 and 10, multiple times for different reasons.
Sometimes the output would be gibberish towards the end, or random NULL lines
in the middle. I solved this using a lock for when I print.

After resolving the printing, I realized that the IDs I was generating for the
cart had collisions (initially, at line 99 `cart_id = cart_id % 1000000` was
set to 10,000)

The most interesting I found out is that list.sort() is atomic

Resurse utilizate
-

1. First three labs from the course.
2. Stackoverflow

Git
-
[1-Marketplace]https://github.com/Lynuxen/asc-public/tree/master/assignments
The submitted version will stay on the `submitted-branch`