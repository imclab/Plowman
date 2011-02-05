#! /usr/bin/env python
# coding=utf-8
"""
Tests for the bookbyline module
"""

import unittest
import sys
sys.path.insert(0, '..')

import bookbyline

class BookTests(unittest.TestCase):

    # create Book and DB instance
    @classmethod
    def setUpClass(cls):
        """ instantiate book and db classes for all tests
        """
        cls._book = bookbyline.BookFromTextFile('test_file.txt', 'This')
        cls._database = bookbyline.DBconn(cls._book.sha, ':memory:')


    # destroy Book and DB instance
    @classmethod
    def tearDownClass(cls):
        """ clean up the classes when we've finished
        """
        del cls._book
        del cls._database


    def setUp(self):
        """ set up known good values to test with
        """
        # provide known correct SHA1 hash of a list of strings
        self.knownValues = ((['a', 'b', 'c', 'd', 'e'],
        '03de6c570bfe24bfc328ccd7ca46b76eadaf4334'),
        )
        # read lines from a test text file
        with open('test_file.txt', 'r') as f:
            self.lines = f.readlines()
        # made-up OAauth values
        self._database.oavals = {}
        self._database.oavals['conkey'] = 'A'
        self._database.oavals['consecret'] = 'B'
        self._database.oavals['acckey'] = 'C'
        self._database.oavals['accsecret'] = 'D'


    def tearDown(self):
        """ empty the database table and remove old known values when each
        test ends
        """
        # ensure we have a clean position table prior to each test
        self._database.cursor.execute(
        'DELETE FROM position'
        )
        self._database.connection.commit()
        del self.knownValues
        del self.lines


    def testDatabaseConnectionExists(self):
        """ should return a valid sqlite3 connection object
        """
        self.assertTrue(type(self._database.connection), 'sqlite3.Connection')


    def testInsertValuesIntoDatabase(self):
        """ should be able to insert rows into the db, and retrieve them
            the db digest value should be the same as the book object's
        """
        self._database._insert_values(self._database.oavals)
        self._database.get_row()
        self.assertEqual(self._database.row[4], self._book.sha)


    def testFormatTweet(self):
        """ will pass if the output var begins with 'This',
        which is the first word of the first line in the test text file,
        and contains the first two words of the second line
        """
        self._database._insert_values(self._database.oavals)
        self._book.get_db(self._database)
        output = self._book.format_tweet()
        self.assertTrue(output.startswith('This'))
        self.assertTrue(output.find('It has') > -1)


    def testWriteValuesToDatabase(self):
        """ will pass if we successfully write updated values to the db
        """
        self._database._insert_values(self._database.oavals)
        self._database.write_vals(33, 45, 'New Header')
        self._database.cursor.execute(
        'SELECT * FROM position'
        )
        r = self._database.cursor.fetchone()
        self.assertEqual(r[1],33)
        self.assertEqual(r[2],45)
        self.assertEqual(r[3],'New Header')


    def testCreateDatabaseConnectionFromBook(self):
        """ ensure that values are returned from db to book object
        """
        self._database._insert_values(self._database.oavals)
        self._book.get_db(self._database)
        self.assertEqual(self._book.oavals['conkey'], 'A')
        self.assertTrue(type(self._book.lines), 'itertools.islice object')


    def testBookByLineHashMethod(self):
        """ should return a SHA1 hash for a given list of strings
        """
        for string, sha_hash in self.knownValues:
            result = bookbyline.get_hash(string)
            self.assertEqual(sha_hash, result)


    def testBookByLineImpFile(self):
        """ should return a tuple
        """
        result = bookbyline.imp_file(self.lines)
        self.assertTrue(type(result) == tuple)


    def testBookByLineTupleContents(self):
        """ tuple should contain no blank lines
        """
        result = bookbyline.imp_file(self.lines)
        for r in result:
            self.assertTrue(r != '\n')


    def testBookFileHashIncorrect(self):
        """ should fail, because the SHA property should be valid
        """
        self.assertNotEqual(self._book.sha, 'abc')


    def testBookFileHashCorrect(self):
        """ class property should be equal to known correct SHA value
            of test_file.txt
        """
        self.assertEqual(
        self._book.sha,
        'dd5c938011a40a91c49ca9564f3aac40b67c8d27')


if __name__ == "__main__":
    unittest.main()