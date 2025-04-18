"""Classes representing certain types of identifier used in the FIRDS data."""
from dataclasses import dataclass

# TODO: Test

class BadIdentifierException(Exception): pass


class BadLeiError(BadIdentifierException): pass


class BadIsinError(BadIdentifierException): pass


@dataclass
class LEI:
    """A Legal Entity Identifier."""

    code: str
    """The LEI code as a string."""
    lou_identifier: str = None
    """The first four digits of the LEI, which identify the local operating unit (LOU) for the LEI."""
    entity_identifier: str = None
    """The fifth to eighteenth digits of the LEI, which identify the entity itself."""
    check_digits: str = None
    """The last two digits of the LEI, which are check digits."""

    def __post_init__(self):
        self.lou_identifier = self.code[:4]
        self.entity_identifier = self.code[4:18]
        self.check_digits = self.code[18:]

    def verify_checksum(self) -> bool:
        """Verify that the LEI's check digits are valid. The alphanumeric LEI code is converted to an integer by
        replacing alphabetical characters with corresponding numbers. If the resulting integer modulo 97 equals 1, the
        checksum is valid.
        """
        base10 = ''.join(str(int(c, 36) for c in self.code))
        return (base10 % 97) == 1

    def validate(self):
        """Perform some basic checks against the LEI code to ensure it broadly looks okay (is the right length, etc),
        and throw an error otherwise. Does not check if the given LEI code has actually been issued.
        """
        lei = self.code
        lei_len = len(lei)
        if lei_len != 20:
            raise BadLeiError(f"LEI must be of length 20, not {lei_len}.")
        if not self.lou_identifier.isalnum():
            raise BadLeiError(f"LOU identifier must be alphanumeric characters, not {self.lou_identifier}.")
        if not self.entity_identifier.isalnum():
            raise BadLeiError(f"Entity identifier must be alphanumeric characters, not {self.entity_identifier}.")
        if not self.check_digits.isdigit():
            raise BadLeiError(f"Checksum digits of LEI must be numbers, not {self.check_digits}.")
        if not self.verify_checksum():
            raise BadLeiError("Checksum validation failed.")


@dataclass
class ISIN:
    """An International Securities Identification Number."""

    code: str
    """The ISIN as a string."""
    country_code: str = None
    """The first two digits of the ISIN, which form a country code."""
    instrument_identifier: str = None
    """Third to eleventh digits of the ISIN, which form an alphanumeric security identifier."""
    check_digit: int = None
    """Last digit of the ISIN, which is a check digit."""

    def __post_init__(self):
        self.country_code = self.code[:2]
        self.instrument_identifier = self.code[2:11]
        self.check_digit = int(self.code[11])

    def verify_checksum(self) -> bool:
        """Verify that the ISIN's check digit is valid."""

        isin = list(self.code.upper()[:-1])
        # Replace country code characters with numbers
        for i, char in enumerate(isin):
            char_pos = ord(char)
            if char_pos in range(65, 91):
                isin[i] = str(ord(char) - 55)
        isin = [int(i) for i in ''.join(isin)]
        # These are considered "odd" and "even" based on a 1-based index
        odd_chars = isin[::2]
        even_chars = isin[1::2]
        if len(isin) % 2:
            # Odd number of characters
            odd_chars = [int(c) for c in ''.join([str(i * 2) for i in odd_chars])]
        else:
            # Even number of characters
            even_chars = [int(c) for c in ''.join([str(i * 2) for i in even_chars])]
        sum_digits = sum(odd_chars + even_chars)
        mod10 = sum_digits % 10
        return ((10 - mod10) % 10) == self.check_digit

    def validate(self):
        """Perform some basic checks against the ISIN code to ensure it broadly looks okay (is the right length, etc),
        and throw an error otherwise. Does not check if the ISIN code has actually been issued.
        """
        isin_len = len(self.code)
        if isin_len != 12:
            raise BadIsinError(f"ISIN must be of length 12, not {isin_len}.")
        if not self.country_code.isalpha():
            raise BadIsinError(f"Country identifier must be country code, not {self.country_code}.")
        if not self.instrument_identifier.isalnum():
            raise BadIsinError(f"Instrument identifier must be alphanumeric, not {self.instrument_identifier}.")
        if not self.verify_checksum():
            raise BadIsinError("Checksum validation failed.")
