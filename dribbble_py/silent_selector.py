class SilentSelector:
    """
    Wrapper class for handling exceptions during scraping of a page soup of bs4
    """

    def __init__(self, page_soup):
        self.page_soup = page_soup

    def select_one(self, query_string: str, get_text: bool, attribute: str):
        """
        Wrapper for select_one() of bs4 with exception handling.

        Arguments:
            query_string: string
            get_text: bool
            attribute: string

        Returns:


        """
        try:
            if get_text:
                return self.page_soup.select_one(query_string).text

            elif attribute is not None:
                return self.page_soup.select_one(query_string).get(attribute)

            else:
                return self.page_soup.select_one(query_string)

        except (AttributeError, TypeError):
            return None

    def select(self, query_string: str):
        """
        Wrapper for select() of bs4 with exception handling.

        Arguments:
            query_string: string
        Returns:


        """
        try:
            return self.page_soup.select(query_string)
        except (AttributeError, TypeError):
            return None

    def find_all(
        self,
        query_tag: str,
        tag_class: str,
        tag_id: str,
        get_string: bool,
        attribute: str,
    ):
        """
        Wrapper for find_all() of bs4 with exception handling.

        Arguments:
            query_tag: string
            tag_class: string
            tag_id: string
            get_string: bool
            attribute: string

        Returns:


        """

        if tag_class is not None:
            if get_string:
                return self.page_soup.find_all(query_tag, class_=tag_class).text

            elif attribute is not None:
                return self.page_soup.find_all(query_tag, class_=tag_class).get(
                    attribute
                )
            else:
                return self.page_soup.find_all(query_tag, class_=tag_class)

        elif tag_id is not None:
            if get_string:
                return self.page_soup.find_all(query_tag, id_=tag_class).text
            elif attribute is not None:
                return self.page_soup.find_all(query_tag, id_=tag_class).get(attribute)
            else:
                return self.page_soup.find_all(query_tag, id_=tag_class)
        elif attribute is not None:
            return self.page_soup.find_all(query_tag).get(attribute)
        else:
            return self.page_soup.find_all(query_tag)

    def find(
        self,
        query_tag: str,
        tag_class: str,
        tag_id: str,
        get_string: bool,
        attribute: str,
    ):
        """
        Wrapper for find() of bs4 with exception handling.

        Arguments:
            query_string: string
            tag_class: string
            tag_id: string
            get_string: bool
            attribute: string

        Returns:


        """

        if tag_class is not None:
            if get_string:
                return self.page_soup.find(query_tag, class_=tag_class).text

            elif attribute is not None:
                return self.page_soup.find(query_tag, class_=tag_class).get(attribute)
            else:
                return self.page_soup.find(query_tag, class_=tag_class)

        elif tag_id is not None:
            if get_string:
                return self.page_soup.find(query_tag, id_=tag_class).text
            elif attribute is not None:
                return self.page_soup.find(query_tag, id_=tag_class).get(attribute)
            else:
                return self.page_soup.find(query_tag, id_=tag_class)
        elif attribute is not None:
            return self.page_soup.find(query_tag).get(attribute)
        else:
            return self.page_soup.find(query_tag)
