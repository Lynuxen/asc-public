"""
This module represents the Marketplace.

Computer Systems Architecture Course
Assignment 1
March 2021
"""

import uuid
import hashlib
import unittest

from threading import Lock, currentThread
from tema.product import Coffee, Tea


class Marketplace:
    """
    Class that represents the Marketplace. It's the central part of the implementation.
    The producers and consumers use its methods concurrently.
    """

    def __init__(self, queue_size_per_producer):
        """
        Constructor

        :type queue_size_per_producer: Int
        :param queue_size_per_producer: the maximum size of a queue associated with each producer
        """

        self.queue_size_per_producer = queue_size_per_producer
        self.queue = []
        self.consumers = {}
        self.producers = {}

        self.mutex = Lock()
        self.prod_mutex = Lock()
        self.cart_mutex = Lock()
        self.print_mutex = Lock()

    def register_producer(self):
        """
        Returns an id for the producer that calls this.
        """
        with self.prod_mutex:
            producer_id = str(uuid.uuid4())
            self.producers[producer_id] = 0
        return producer_id

    def publish(self, producer_id, product):
        """
        Adds the product provided by the producer to the marketplace

        :type producer_id: String
        :param producer_id: producer id

        :type product: Product
        :param product: the Product that will be published in the Marketplace

        :returns True or False. If the caller receives False, it should wait and then try again.
        """
        if self.producers[producer_id] < self.queue_size_per_producer:
            self.queue.append((product, producer_id))
            self.producers[producer_id] += 1
            return True

        return False

    def new_cart(self):
        """
        Creates a new cart for the consumer

        :returns an int representing the cart_id
        """
        random_cart_id = str(uuid.uuid4())
        hashed_cart_id = hashlib.sha256(random_cart_id.encode())
        cut_down_hex = hashed_cart_id.hexdigest()[:8]
        cart_id = int(cut_down_hex, 16)
        cart_id = cart_id % 10000
        self.consumers[cart_id] = []
        return cart_id

    def add_to_cart(self, cart_id, product):
        """
        Adds a product to the given cart. The method returns

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to add to cart

        :returns True or False. If the caller receives False, it should wait and then try again
        """

        first_product = next((x for x in self.queue if x[0] == product), None)
        if isinstance(first_product, tuple):
            self.consumers[cart_id].append(first_product)
            with self.cart_mutex:
                self.queue.remove(first_product)
                self.producers[first_product[1]] -= 1
            return True

        return False

    def remove_from_cart(self, cart_id, product):
        """
        Removes a product from cart.

        :type cart_id: Int
        :param cart_id: id cart

        :type product: Product
        :param product: the product to remove from cart
        """

        first_product = next(
            (x for x in self.consumers[cart_id] if x[0] == product), None)
        if isinstance(first_product, tuple):
            self.queue.append(first_product)
            with self.cart_mutex:
                self.consumers[cart_id].remove(first_product)
                self.producers[first_product[1]] += 1

    def place_order(self, cart_id):
        """
        Return a list with all the products in the cart.

        :type cart_id: Int
        :param cart_id: id cart
        """

        for product in self.consumers[cart_id]:
            with self.print_mutex:
                print(
                    f"{currentThread().getName()} bought {product[0]}")
        return self.consumers[cart_id]


class TestMarketplace(unittest.TestCase):
    def setUp(self):
        self.limit = 5
        self.marketplace = Marketplace(self.limit)
        self.products = [Coffee("Indonezia", 1, 5.05, "MEDIUM"),
                         Tea("White Peach", 5, "White"),
                         Coffee("Brasil", 7, 5.09, "MEDIUM"),
                         Coffee("Ethiopia", 10, 5.09, "MEDIUM"),
                         Tea("Vietnam Oolong", 10, "Oolong")]

    def test_register_producer(self):
        """
        Registers five producers and checks if the number is set to 0.
        """
        producers_id = []
        for x in range(5):
            producers_id.append(self.marketplace.register_producer())

            self.assertEqual(self.marketplace.producers[producers_id[x]], 0,
                             "Producer not initialized correctly!")
        return producers_id

    def test_publish(self):
        """
        Tests if a producer can publish and checks against the limit.
        """
        producers_id = self.test_register_producer()
        for single_id in producers_id:
            # fill the limit
            for x in range(self.limit):
                ret = self.marketplace.publish(single_id, self.products[x])
                self.assertTrue(
                    ret, "The producer should publish these products")
                ret = len(self.marketplace.queue)
                self.assertTrue(ret * x + 1, "Product has not been published!")
            # check if limit is working correctly
            for x in range(self.limit):
                ret = self.marketplace.publish(single_id, self.products[x])
                self.assertFalse(
                    ret, "The producer should NOT publish these products!")

    def test_new_cart(self):
        """
        Tests to see if each cart has a unique int identifier and has been
        properly initialized.
        """
        cart_ids = []
        for x in range(10):
            ret = self.marketplace.new_cart()
            self.assertTrue(isinstance(ret, int), "IDs are NOT ints!")
            cart_ids.append(ret)
            self.assertEqual(self.marketplace.consumers[cart_ids[x]], [],
                             "Lists have not been properly initialized!")

        ret = len(cart_ids) == len(set(cart_ids))
        self.assertTrue(ret, "All IDs are NOT unique!")
        return cart_ids

    def test_add_to_cart(self):
        """
        Tests add_to_cart functionality
        """
        # There are no items published, so we shouldnt be able to add the product
        producers_id = self.test_register_producer()
        cart_ids = self.test_new_cart()

        self.assertFalse(self.marketplace.add_to_cart(cart_ids[0], self.products[0]),
                         "Product should NOT be available!")

        self.marketplace.publish(producers_id[0], self.products[0])

        self.assertTrue(self.marketplace.add_to_cart(cart_ids[0], self.products[0]),
                         "Product should be added!")
        ret = len(self.marketplace.consumers[cart_ids[0]]) > 0
        self.assertTrue(ret, "Product NOT added to cart!")
        
    def test_remove_from_cart(self):
        """
        Tests removing an item from the cart
        """
        cart_ids = self.test_new_cart()
        
        if self.marketplace.add_to_cart(cart_ids[0], self.products[0]):
            self.marketplace.remove_from_cart(cart_ids[0], self.products[0])
            ret = len(self.marketplace.consumers[cart_ids]) > 0
            self.assertTrue(ret, "Product has NOT been removed!")

        if self.marketplace.add_to_cart(cart_ids[0], self.products[0]):
            self.marketplace.remove_from_cart(cart_ids[0], self.products[1])
            ret = len(self.marketplace.consumers[cart_ids]) == 0
            self.assertTrue(ret, "Product has been removed!")


    def test_place_order(self):
        """
        Tests place_order.
        """
        producer_ids = self.test_register_producer()
        cart_ids = self.test_new_cart()

        for x in self.products:
            self.marketplace.publish(producer_ids[0], x)
            self.marketplace.add_to_cart(cart_ids[0], x)

        
        ret = self.marketplace.place_order(cart_ids[0])

        for x in range(5):
            self.assertEqual(ret[x][0], self.products[x],
                             "Not the expected products!")
