"""
THIS IS THE TREE CONSTRUCTION STAGE AS SPECIFIED IN THE SPECIFICATION HERE:
https://html.spec.whatwg.org/multipage/parsing.html#tree-construction
"""
from src.browser_engine.html_lib.structures.DOM import *
from src.browser_engine.html_lib.structures.TOKENS import *
from src.browser_engine.html_lib.tokenizer import HTMLTokenizer
from src.browser_engine.helpers.CONSTANTS import *
from src.browser_engine.helpers.funcs import is_whitespace


class TokenStream:
    def __init__(self, source):
        self.tokenizer = HTMLTokenizer(source)
        self.token_generator = self.tokenizer.tokenize()
        self.current_token = None

        self.reprocessing = False
        self.out_of_tokens = False

    def next(self):
        if self.reprocessing:
            return self.reprocess()
        try:
            self.current_token = next(self.token_generator)
        except StopIteration:
            self.out_of_tokens = True
            self.current_token = EOFToken()

        return self.current_token

    def reprocess(self):
        self.reprocessing = False
        return self.current_token

    def is_truly_out_of_index(self):
        return self.out_of_tokens and not self.reprocessing


# noinspection PyMethodMayBeStatic
class HTMLParser:
    base_scope_list = ["applet", "caption", "html", "table", "td", "th", "marquee", "object", "template", "mi", "mo",
                       "mn", "ms", "mtext", "annotation-xml", "foreignObject", "desc", "title"]

    def __init__(self, source):
        self.token_stream = TokenStream(source)
        self.tokenizer = self.token_stream.tokenizer

        # STATE VARIABLES
        self.insertion_mode = self.initial_mode
        self.original_insertion_mode = None
        self.stack_of_open_elems = []

        self.parsing_finished = False

        # STATE FLAGS
        self.foster_parenting = False  # FOSTER PARENTING OCCURS DUE TO INCORRECT NESTING OF TAGS
        self.created_as_fragment_parser = False  # POSSIBLE BUG: POSSIBLY WRONG IMPLEMENTATION
        self.frameset_ok_flag = True  # True is "ok", False is "not ok" (idk why it's used, defined just for compliance)
        self.parser_cannot_change_mode = False

        # ELEMENT POINTERS
        self.head_pointer = None
        self.last_form_pointer = None  # the last form element that was opened, and has not yet reached it's end tag

        # OUTPUT
        self.document = Document()
        self.errors = 0

    # PROPERTIES
    def current_node(self, step=-1):
        try:
            return self.stack_of_open_elems[step]
        except IndexError:
            return None

    def adjusted_current_node(self):
        # TODO: PARTIALLY IMPLEMENTED METHOD
        if self.created_as_fragment_parser:
            context_element = None  # TODO: CONTEXT ELEMENT TO BE IMPLEMENTED WHEN FRAGMENT PARSER IS IMPLEMENTED
            return context_element
        else:
            return self.current_node()

    # ALGORITHMS
    def parse_error(self):
        self.errors += 1

    def appropriate_place_for_node_insertion(self, override_target=None):
        """
        # TODO: COMPLETE appropriate_place_Fore_node_insertion()
        RETURNS A DICT {AN ELEMENT, POSITION TO INSERT INTO ELEMENT'S CHILDREN LIST}

        EXAMPLE: TO INSERT AS THE LAST CHILD OF THE HTML ELEMENT:
        (
            # since first element in this stack is always the html element
            "insertion_node": self.stack_of_open_elems[0],
            "insertion_location": -1
        )
        """
        if override_target is not None:
            target = override_target
        else:
            target = self.current_node()

        if self.foster_parenting and target.type in ["table", "tbody", "tfoot", "thead", "tr"]:
            # STEP 1, 2
            last_template, last_table = None, None
            last_template_position, last_table_position = None, None

            reversed_range_for_open_element_stack = reversed(range(len(self.stack_of_open_elems)))
            for position in reversed_range_for_open_element_stack:
                element = self.stack_of_open_elems[position]

                last_template_found = element.type == "template" and last_template is None
                last_table_found = element.type == "table" and last_table is None

                if last_template_found:
                    last_template = element
                    last_template_position = position
                if last_table_found:
                    last_table = element
                    last_table_position = position

                both_elements_found = last_template is not None and last_table is not None
                if both_elements_found:
                    break

            # STEP 3
            last_template_exists, last_table_exists = last_template is not None, last_table is not None
            template_node_level_higher_than_table = last_template_position > last_table_position
            if last_template_exists and \
                    (not last_table_exists or last_table_exists and template_node_level_higher_than_table):
                raise NotImplementedError

            # STEP 4
            elif not last_table_exists:
                adjusted_insertion_location = {
                    "insertion_node": self.stack_of_open_elems[0],
                    "insertion_location": -1
                }
                return adjusted_insertion_location

            # STEP 5 (is possibly misinterpreted here)
            elif last_table.parent is not None:
                adjusted_insertion_location = {
                    "insertion_node": last_table.parent,
                    "insertion_location": last_table.parent.find_child(last_table) - 1
                }
                return adjusted_insertion_location

            # STEP 6
            else:
                previous_element = self.stack_of_open_elems[last_table_position - 1]
                adjusted_insertion_location = {
                    "insertion_node": previous_element,
                    "insertion_location": -1
                }
        else:
            adjusted_insertion_location = {
                "insertion_node": target,
                "insertion_location": -1
            }

        if adjusted_insertion_location["insertion_node"].type == "template":
            raise NotImplementedError

        return adjusted_insertion_location

    def create_element_for_token(self, token, namespace, intended_parent):
        document = intended_parent.root()
        local_name = token.tag_name
        try:
            is_value = token.attributes["is"]
        except (KeyError, IndexError, TypeError):
            is_value = None

        definition = self.lookup_custom_element_definition(document, namespace, local_name, is_value)

        will_execute_script = False
        if definition is not None and not self.created_as_fragment_parser:
            will_execute_script = True

        if will_execute_script:
            raise NotImplementedError

        element = self.create_element(document, local_name, namespace, None, is_value, will_execute_script)
        element.attributes = token.attributes

        if will_execute_script:
            raise NotImplementedError

        # POSSIBLE BUG: SKIPPING SEEMINGLY UNNECESSARY STEPS

        return element

    def insert_a_foreign_element(self, token, namespace):
        adjusted_insertion_location = self.appropriate_place_for_node_insertion()
        insertion_node = adjusted_insertion_location["insertion_node"]
        insertion_location = adjusted_insertion_location["insertion_location"]
        element = self.create_element_for_token(token, namespace, insertion_node)

        # POSSIBLE BUG: NOT SURE IF THIS IS THE RIGHT CONDITION FOR THE CLAUSE
        possible_to_insert_at_insertion_location = not (
                insertion_node.type == "document" and len(insertion_node.children) >= 1
        )
        if possible_to_insert_at_insertion_location:
            if not self.created_as_fragment_parser:
                # TODO: IMPLEMENT ELEMENT QUES
                pass

            insertion_node.insert_child(element, insertion_location)

            if not self.created_as_fragment_parser:
                # TODO: IMPLEMENT ELEMENT QUES
                pass

        self.stack_of_open_elems.append(element)
        return element

    def insert_html_element(self, token):
        return self.insert_a_foreign_element(token, HTML_NAMESPACE)

    def adjust_foreign_attributes(self):
        # TODO: IMPLEMENT ADJUST FOREIGN ATTRIBUTES ALGORITHM
        return

    def insert_character(self, data=None):
        if data is None:
            data = self.token_stream.current_token

        adjusted_insertion_location = self.appropriate_place_for_node_insertion()

        insertion_node = adjusted_insertion_location["insertion_node"]
        insertion_location = adjusted_insertion_location["insertion_location"]
        if insertion_node.type == "document":
            return  # function doesn't return anything, just used to abort here

        preceding_element = self.stack_of_open_elems.index(insertion_node) - 1
        preceding_element = self.stack_of_open_elems[preceding_element]
        insertion_node_succeeds_text_element = preceding_element.type == "text"
        if insertion_node_succeeds_text_element:
            preceding_element.data += data

        else:
            new_text_node = TextNode(data=data)
            insertion_node.insert_child(new_text_node, insertion_location)  # insert_child(what, where)

    def generic_rcdata_element_parsing_algorithm(self, token):
        self.insert_html_element(token)
        self.tokenizer.state = self.tokenizer.rcdata_state

        self.original_insertion_mode = self.insertion_mode
        self.insertion_mode = self.text_mode

    def generic_raw_text_element_parsing_algorithm(self, token):
        self.insert_html_element(token)
        self.tokenizer.state = self.tokenizer.raw_text_state

        self.original_insertion_mode = self.insertion_mode
        self.insertion_mode = self.text_mode

    def generate_implied_end_tags(self, excluded_element=None):
        tags_with_implied_end = ["dd", "dt", "li", "optgroup", "option", "p", "rb", "rp", "rt", "rtc"]
        if excluded_element is not None:
            tags_with_implied_end.remove(excluded_element)
        while self.current_node().type in tags_with_implied_end:
            self.stack_of_open_elems.pop()

    def parse_foreign_content(self):
        token = self.token_stream.next()

        if token.type == "character":
            if token.data == NULL:
                self.parse_error()
                self.insert_character(REPLACEMENT_CHARACTER)

            elif all([char in WHITESPACE for char in token.data]):
                self.insert_character(token.data)

            else:
                self.insert_character(token.data)
                self.frameset_ok_flag = False

        elif token.type == "comment":
            raise NotImplementedError

        elif token.type == "DOCTYPE":
            self.parse_error()
            return  # ignore

        elif token.type == "start tag":
            # POSSIBLE BUGS IN THE IF CLAUSE
            has_expected_font_attrs = all([attr in token.attributes.keys() for attr in ["color", "face", "size"]])
            if token.tag_name in UNACCEPTED_TAGS_IN_FOREIGN_CONTENT or \
                    (token.tag_name == "font" and has_expected_font_attrs):
                self.parse_error()
                current_elem = self.current_node()
                while current_elem not in MATH_ML_TEXT_INTEGRATION_POINTS \
                        or not is_html_integration_point(current_elem) or \
                        current_elem.namespace == HTML_NAMESPACE:
                    self.stack_of_open_elems.pop()

                self.token_stream.reprocessing = True
                return  # parse using the current insertion mode

            else:
                if self.adjusted_current_node().namespace in MATH_ML_NAMESPACE:
                    raise NotImplementedError

                if self.adjusted_current_node().namespace in SVG_NAMESPACE:
                    raise NotImplementedError

                self.adjust_foreign_attributes()

    # EXTRA ALGORITHMS
    # noinspection PyUnusedLocal
    def lookup_custom_element_definition(self, document, namespace, local_name, is_value):
        # TODO: IMPLEMENT LOOKING UP CUSTOM ELEMENT DEFINITIONS
        return None

    def create_element(self, document, local_name, namespace, prefix=None, is_value=None,
                       synchronous_custom_elements_flag=False):
        result = None
        # noinspection PyNoneFunctionAssignment
        definition = self.lookup_custom_element_definition(document, namespace, local_name, is_value)
        # noinspection PyUnresolvedReferences
        definition_represents_custom_element = definition is not None and definition.name != local_name
        if definition_represents_custom_element:
            raise NotImplementedError

        elif definition is not None:
            raise NotImplementedError

        else:
            result = Element(local_name)
            result.namespace = namespace
            result.namespace_prefix = prefix
            result.local_name = local_name
            result.custom_element_state = "uncustomized"
            result.custom_element_definition = None
            result.is_value = is_value
        return result

    def reconstruct_active_formatting_elements(self):
        # TODO: COMPLETE ACTIVE FORMATTING ELEMENTS
        pass

    def has_element_in_specific_scope(self, target_node_type, scope_list):
        for step in range(len(self.stack_of_open_elems)):
            node = self.current_node(step)
            if node.type == target_node_type:
                return True
            elif node.type in scope_list:
                return False

    def has_element_in_scope(self, target_node_type):
        return self.has_element_in_specific_scope(target_node_type, self.base_scope_list)

    def has_element_in_list_item_scope(self, target_node_type):
        scope = self.base_scope_list + ["ol", "li"]
        return self.has_element_in_specific_scope(target_node_type, scope)

    def has_element_in_button_scope(self, target_node_type):
        scope = self.base_scope_list + ["button"]
        return self.has_element_in_specific_scope(target_node_type, scope)

    def close_p_element(self):
        self.generate_implied_end_tags("p")
        if self.current_node().type != "p":
            self.parse_error()
            current_node_is_p_element = True
            while current_node_is_p_element:
                try:
                    current_node_is_p_element = self.current_node().type == "p"
                except AttributeError:
                    current_node_is_p_element = False
                    break
                self.stack_of_open_elems.pop()
        else:
            self.stack_of_open_elems.pop()

    # MAIN LOOP
    def dispatch_token(self):
        try:
            element_is_in_html_namespace = self.adjusted_current_node().namespace == HTML_NAMESPACE,
        except AttributeError:
            element_is_in_html_namespace = True

        conditions_for_parsing_in_current_insertion_mode = [
            len(self.stack_of_open_elems) == 0,
            element_is_in_html_namespace,
            # TODO: SKIPPING SEEMINGLY UNNECESSARY CONDITIONS IN DISPATCHER
            self.token_stream.current_token.type == "eof"
        ]

        if conditions_for_parsing_in_current_insertion_mode:
            self.insertion_mode()
        else:
            self.parse_foreign_content()

    def parse(self):
        # THIS IS AN HACKISH APPROACH TO PROCESS TOKENS (BASICALLY IGNORES THE PARSING IN FOREIGN CONTENT ALGORITHM)
        while not self.token_stream.is_truly_out_of_index():
            print(str(self.insertion_mode)[25:].split('of')[0].upper().replace("_", " "))
            self.insertion_mode()
            if self.parsing_finished:
                break

    # INSERTION MODES
    def initial_mode(self):
        token = self.token_stream.next()

        if token.type == "character" and token.data in WHITESPACE:
            return  # ignore

        elif token.type == "comment":
            raise NotImplementedError

        elif token.type == "DOCTYPE":
            raise NotImplementedError

        else:
            if self.document.type != "iframe srcdoc":
                self.parse_error()

            if self.parser_cannot_change_mode:
                self.document.mode = "quirks-mode"

            self.insertion_mode = self.before_html_mode
            self.token_stream.reprocessing = True

    def before_html_mode(self):
        token = self.token_stream.next()

        if token.type == "DOCTYPE":
            self.parse_error()
            return  # ignore

        elif token.type == "comment":
            raise NotImplementedError

        elif token.type == "character" and is_whitespace(token.data):
            return  # ignore

        elif token.type == "start tag" and token.tag_name == "html":
            html_element = self.create_element_for_token(token, HTML_NAMESPACE, self.document)
            self.document.append_child(html_element)
            self.stack_of_open_elems.append(html_element)
            self.insertion_mode = self.before_head_mode

        elif token.type == "end tag" and token.tag_name not in ["head", "body", "br"]:
            self.parse_error()
            return  # ignore

        else:
            html_element = self.create_element(self.document, "html", HTML_NAMESPACE)
            html_element.type = "html"
            self.document.append_child(html_element)
            self.stack_of_open_elems.append(html_element)

            self.insertion_mode = self.before_head_mode
            self.token_stream.reprocessing = True

    def before_head_mode(self):
        token = self.token_stream.next()

        if token.type == "character" and is_whitespace(token.data):
            return  # ignore

        elif token.type == "comment":
            raise NotImplementedError

        elif token.type == "start tag" and token.tag_name == "html":
            self.token_stream.reprocessing = True
            self.in_body_mode()

        elif token.type == "start tag" and token.tag_name == "head":
            head_element = self.insert_html_element(token)
            self.head_pointer = head_element

            self.insertion_mode = self.in_head_mode

        elif token.type == "end tag" and token.tag_name not in ["head", "body", "html", "br"]:
            self.parse_error()
            return  # ignore

        else:
            head_token = StartTagToken("head")
            head_token.convert_attrs_to_dict()
            head_element = self.insert_html_element(head_token)
            self.head_pointer = head_element

            self.insertion_mode = self.in_head_mode
            self.token_stream.reprocessing = True

    def in_head_mode(self):
        token = self.token_stream.next()
        tag_name = token.tag_name
        is_start_tag, is_end_tag = token.type == "start tag", token.type == "end tag"

        if token.type == "character" and is_whitespace(token.data):
            self.insert_character(token.data)

        elif token.type == "comment":
            raise NotImplementedError

        elif token.type == "DOCTYPE":
            self.parse_error()
            return  # ignore

        elif is_start_tag and tag_name == "html":
            self.token_stream.reprocessing = True
            self.in_body_mode()

        elif is_start_tag and tag_name in ["base", "basefont", "bgsound", "link"]:
            self.insert_html_element(token)
            self.stack_of_open_elems.pop()

        elif is_start_tag and tag_name == "meta":
            self.insert_html_element(token)
            self.stack_of_open_elems.pop()
            # POSSIBLE BUG: SKIPPED ENCODING HANDLING HERE (SEEMED UNNECESSARY)

        elif is_start_tag and tag_name == "title":
            self.generic_rcdata_element_parsing_algorithm(token)

        # TODO: SKIPPING NOSCRIPT TAG CLAUSES HERE, COMPLETE WHEN SCRIPTING SUPPORT IS REQUIRED

        elif is_start_tag and tag_name == "script":
            raise NotImplementedError

        elif is_end_tag and tag_name == "head":
            self.stack_of_open_elems.pop()
            self.insertion_mode = self.after_head_mode

        elif is_end_tag and tag_name in ["body", "html", "br"]:
            self.stack_of_open_elems.pop()
            self.insertion_mode = self.after_head_mode
            self.token_stream.reprocessing = True

        elif is_start_tag and tag_name == "template":
            raise NotImplementedError

        elif is_end_tag and tag_name == "template":
            raise NotImplementedError

        elif is_end_tag or (is_start_tag and tag_name == "head"):
            self.parse_error()
            return  # ignore

        else:
            self.stack_of_open_elems.pop()
            self.insertion_mode = self.after_head_mode
            self.token_stream.reprocessing = True

    def after_head_mode(self):
        token = self.token_stream.next()
        tag_name = token.tag_name
        is_start_tag, is_end_tag = token.type == "start tag", token.type == "end tag"

        if token.type == "character" and is_whitespace(token.data):
            self.insert_character(token.data)

        elif token.type == "comment":
            raise NotImplementedError

        elif token.type == "DOCTYPE":
            self.parse_error()
            return  # ignore

        elif is_start_tag and tag_name == "html":
            self.token_stream.reprocessing = True
            self.in_body_mode()

        elif is_start_tag and tag_name == "body":
            self.insert_html_element(token)
            self.frameset_ok_flag = False
            self.insertion_mode = self.in_body_mode

        elif is_start_tag and tag_name == "frameset":
            raise NotImplementedError

        elif is_start_tag and tag_name in ["base", "basefont", "bgsound", "link", "meta", "noframes", "script", "style",
                                           "template", "title"]:
            self.parse_error()
            self.stack_of_open_elems.append(self.head_pointer)
            self.token_stream.reprocessing = True
            self.in_head_mode()
            self.stack_of_open_elems.remove(self.head_pointer)

        elif is_end_tag and tag_name == "template":
            self.token_stream.reprocessing = True
            self.in_head_mode()

        elif (is_end_tag and tag_name not in ["body", "html", "br"]) or is_start_tag and tag_name == "head":
            self.parse_error()
            return  # ignore

        else:
            body_token = StartTagToken("body")
            body_token.convert_attrs_to_dict()
            self.insert_html_element(body_token)
            self.insertion_mode = self.in_body_mode
            self.token_stream.reprocessing = True

    def in_body_mode(self):
        token = self.token_stream.next()
        # these are checked too often, so decided to store in variables
        tag_name = token.tag_name
        is_start_tag, is_end_tag = token.type == "start tag", token.type == "end tag"

        unacceptable_elements = ["dd", "dt", "li", "optgroup", "option", "p", "rb", "rp", "rt", "rtc", "tbody",
                                 "td", "tfoot", "th", "thead", "tr", "body", "html"]

        if token.type == "character":
            if token.data == NULL:
                self.parse_error()
                return  # ignore

            elif is_whitespace(token.data):
                self.reconstruct_active_formatting_elements()

                self.insert_character(token.data)

            else:
                self.reconstruct_active_formatting_elements()
                self.insert_character(token.data)
                self.frameset_ok_flag = False

        elif token.type == "comment":
            raise NotImplementedError

        elif token.type == "DOCTYPE":
            self.parse_error()
            return  # ignore

        elif is_start_tag and tag_name == "html":
            self.parse_error()
            # FIXME: SKIPPED STEPS HERE

        elif (is_start_tag and tag_name in ["base", "basefont", "bgsound", "link", "meta", "noframes", "script",
                                            "style", "template", "title"]) or \
                (is_end_tag and tag_name == "template"):
            self.token_stream.reprocessing = True
            self.in_head_mode()

        elif is_start_tag and tag_name == "body":
            self.parse_error()

            second_element_in_stack_is_not_body = not self.stack_of_open_elems[1].type == "body"
            stack_has_only_one_node = len(self.stack_of_open_elems) == 1
            template_element_in_stack = False
            for node in self.stack_of_open_elems[::-1]:
                if node.type == "template":
                    template_element_in_stack = True
                    break
            fragment_case = second_element_in_stack_is_not_body or stack_has_only_one_node or template_element_in_stack

            if fragment_case:
                return  # ignore
            else:
                self.frameset_ok_flag = False
                body_element = self.stack_of_open_elems[1]
                body_attrs = body_element.keys()
                for attr_name, attr_value in token.attributes.items():
                    if attr_name not in body_attrs:
                        body_element.attributes[attr_name] = attr_value

        elif is_start_tag and tag_name == "frameset":
            raise NotImplementedError

        elif token.type == "EOF":
            # FIXME: SKIPPING STACK OF TEMPLATE INSERTION MODES CHECK HERE

            stack_has_unacceptable_element = False
            for node in self.stack_of_open_elems:
                if node.type in unacceptable_elements:
                    stack_has_unacceptable_element = True

            if stack_has_unacceptable_element:
                self.parse_error()

            self.parsing_finished = True

        elif is_end_tag and tag_name == "body":
            if not self.has_element_in_scope("body"):
                self.parse_error()
                return  # ignore

            for node in self.stack_of_open_elems[::-1]:
                if node.type in unacceptable_elements:
                    self.parse_error()
                    break

            self.insertion_mode = self.after_body

        elif is_end_tag and tag_name == "html":
            if not self.has_element_in_scope("body"):
                self.parse_error()
                return  # ignore
            for node in self.stack_of_open_elems[::-1]:
                if node.type in unacceptable_elements:
                    self.parse_error()
                    break

            self.insertion_mode = self.after_body
            self.token_stream.reprocessing = True

        elif is_start_tag and tag_name in ["address", "article", "aside", "blockquote", "center", "details", "dialog",
                                           "dir", "div", "di", "fieldset", "figcaption", "figure", "footer", "header",
                                           "hgroup", "main", "menu", "nav", "ol", "p", "section", "summary", "ul"]:
            if self.has_element_in_button_scope("p"):
                self.close_p_element()

            self.insert_html_element(token)

        elif is_start_tag and tag_name in ["h1", "h2", "h3", "h4", "h5", "h6"]:
            if self.has_element_in_button_scope("p"):
                self.close_p_element()

            current_node = self.current_node()
            unacceptable_node = current_node.namespace == HTML_NAMESPACE and current_node.type in ["h1", "h2", "h3",
                                                                                                   "h4", "h5", "h6"]
            if unacceptable_node:
                self.parse_error()
                self.stack_of_open_elems.pop()

            self.insert_html_element(token)

        elif is_start_tag and tag_name in ["pre", "listing"]:
            raise NotImplementedError

        elif is_start_tag and tag_name == "form":
            raise NotImplementedError

        elif is_start_tag and tag_name == "li":
            raise NotImplementedError

        elif is_start_tag and tag_name in ["dd", "dt"]:
            raise NotImplementedError

        elif is_start_tag and tag_name == "plaintext":
            if self.has_element_in_button_scope("p"):
                self.close_p_element()

            self.insert_html_element(token)
            self.tokenizer.state = self.tokenizer.plaintext_state

        elif is_start_tag and tag_name == "button":
            if self.has_element_in_scope("button"):
                self.parse_error()
                self.generate_implied_end_tags()
                while self.current_node().type != "button":
                    self.stack_of_open_elems.pop()
                self.stack_of_open_elems.pop()
            self.reconstruct_active_formatting_elements()
            self.insert_html_element(token)
            self.frameset_ok_flag = False

        elif is_end_tag and tag_name in ["address", "article", "aside", "blockquote", "button", "center", "details",
                                         "dialog", "dir", "div", "dl", "fieldset", "figcaption", "figure", "footer",
                                         "header", "hgroup", "listing", "main", "menu", "nav", "ol", "pre", "section",
                                         "summary", "ul"]:
            if self.has_element_in_scope(tag_name):
                self.parse_error()
                return  # ignore

            self.generate_implied_end_tags()
            if self.current_node().namespace != HTML_NAMESPACE and self.current_node().type != tag_name:
                self.parse_error()

            current_node_matches_tag_name = True
            while current_node_matches_tag_name:
                try:
                    current_node_matches_tag_name = self.current_node().type == tag_name
                except AttributeError:
                    current_node_matches_tag_name = False
                    break
                self.stack_of_open_elems.pop()

        elif is_end_tag and tag_name == "form":
            raise NotImplementedError

        elif is_end_tag and tag_name == "p":
            if not self.has_element_in_button_scope("p"):
                self.parse_error()
                self.insert_html_element(StartTagToken().emit_to(self.tokenizer))
                self.close_p_element()

        elif is_end_tag and tag_name == "li":
            if self.has_element_in_list_item_scope("li"):
                self.parse_error()
                return  # ignore

            self.generate_implied_end_tags("li")
            if self.current_node().type != "li":
                self.parse_error()
            while self.current_node().type != "li":
                self.stack_of_open_elems.pop()
            self.stack_of_open_elems.pop()

        elif is_end_tag and tag_name in ["dd", "dt"]:
            if not self.has_element_in_scope(tag_name):
                self.parse_error()
                return  # ignore

            self.generate_implied_end_tags(tag_name)
            if self.current_node().type != tag_name:
                self.parse_error()
            while self.current_node().type != tag_name:
                self.stack_of_open_elems.pop()
            self.stack_of_open_elems.pop()

        elif is_end_tag and tag_name in ["h1", "h2", "h3", "h4", "h5"]:
            has_element_in_scope = False
            for h in ["h1", "h2", "h3", "h4", "h5"]:
                if self.has_element_in_scope(h):
                    has_element_in_scope = True
                    break

            if not has_element_in_scope:
                self.parse_error()
                return  # ignore

            self.generate_implied_end_tags()
            if self.current_node().type != tag_name:
                self.parse_error()
            while self.current_node().type not in ["h1", "h2", "h3", "h4", "h5"]:
                self.stack_of_open_elems.pop()
            self.stack_of_open_elems.pop()

        elif is_start_tag and tag_name == "a":
            raise NotImplementedError

        elif is_start_tag and tag_name in ["b", "big", "code", "em", "font", "i", "s", "small", "strike", "strong",
                                           "tt", "u"]:
            raise NotImplementedError

        elif is_start_tag and tag_name == "nobr":
            raise NotImplementedError

        elif is_end_tag and tag_name in ["a", "b", "big", "code", "em", "font", "i", "nobr", "s", "small", "strike",
                                         "strong", "tt", "u"]:
            raise NotImplementedError

        elif is_start_tag and tag_name in ["applet", "marquee", "object"]:
            raise NotImplementedError

        elif is_end_tag and tag_name in ["applet", "marquee", "object"]:
            raise NotImplementedError

        elif is_start_tag and tag_name == "table":
            if self.document.mode != "quirks-mode" and self.has_element_in_button_scope("p"):
                self.close_p_element()

            self.insert_html_element(token)
            self.frameset_ok_flag = False
            self.insertion_mode = self.in_table

        elif is_end_tag and tag_name == "br":
            self.parse_error()
            token = StartTagToken("br").emit_to(self.tokenizer)
            self.reconstruct_active_formatting_elements()
            self.insert_html_element(token)
            self.stack_of_open_elems.pop()
            self.frameset_ok_flag = False

        elif is_start_tag and tag_name in ["area", "br", "embed", "img", "keygen", "wbr"]:
            token = StartTagToken("br").emit_to(self.tokenizer)
            self.reconstruct_active_formatting_elements()
            self.insert_html_element(token)
            self.stack_of_open_elems.pop()
            self.frameset_ok_flag = False

        elif is_start_tag and tag_name == "input":
            token = StartTagToken("br").emit_to(self.tokenizer)
            self.reconstruct_active_formatting_elements()
            self.insert_html_element(token)
            self.stack_of_open_elems.pop()
            try:
                self.frameset_ok_flag = token.attributes["type"].lower() == "hidden"
            except KeyError:
                # just for readability (i.e. let the flag be whatever it was before)
                self.frameset_ok_flag = self.frameset_ok_flag

        elif is_start_tag and tag_name in ["param", "source", "track"]:
            self.insert_html_element(token)
            self.stack_of_open_elems.pop()

        elif is_start_tag and tag_name == "hr":
            if self.has_element_in_button_scope("p"):
                self.close_p_element()

            self.insert_html_element(token)
            self.stack_of_open_elems.pop()
            self.frameset_ok_flag = False

        elif is_start_tag and tag_name == "image":
            self.parse_error()
            # To quote html spec authors: "don't ask" just don't. 😂
            self.token_stream.current_token.tag_name = "img"
            self.token_stream.reprocessing = True

        elif is_start_tag and tag_name == "textarea":
            self.insert_html_element(token)
            next_token = self.token_stream.next()
            self.token_stream.reprocessing = True
            if next_token.type == "character" and all([char == NEWLINE for char in token.data]):
                return  # ignore the token

            self.tokenizer.state = self.tokenizer.rcdata_state
            self.original_insertion_mode = self.insertion_mode
            self.frameset_ok_flag = False
            self.insertion_mode = self.text_mode

        elif is_start_tag and tag_name == "xmp":
            if self.has_element_in_button_scope("p"):
                self.close_p_element()

            self.reconstruct_active_formatting_elements()
            self.frameset_ok_flag = False
            self.generic_raw_text_element_parsing_algorithm(token)

        elif is_start_tag and tag_name == "iframe":
            self.frameset_ok_flag = False
            self.generic_raw_text_element_parsing_algorithm(token)

        elif is_start_tag and tag_name in ["noembed", "noscript"]:  # also requires check for scripting flag but skipped
            self.generic_raw_text_element_parsing_algorithm(token)

        elif is_start_tag and tag_name == "select":
            self.reconstruct_active_formatting_elements()
            raise NotImplementedError
            # self.insert_html_element(token)
            # self.frameset_ok_flag = False
            # states_to_check_for = [self.in_table_mode, self.in_caption_mode, self.in_table_body_mode,
            #                        self.in_row_mode, self.in_cell_mode]
            # if self.insertion_mode in states_to_check_for:
            #     self.insertion_mode = self.in_select_in_table_mode
            # else:
            #     self.insertion_mode = self.in_select_mode

        elif is_start_tag and tag_name in ["optgroup", "option"]:
            raise NotImplementedError

        elif is_start_tag and tag_name in ["rb", "rtc"]:
            if self.has_element_in_scope("ruby"):
                self.generate_implied_end_tags()
                if self.current_node().type != "ruby":
                    self.parse_error()
            self.insert_html_element(token)

        elif is_start_tag and tag_name in ["rp", "rt"]:
            if self.has_element_in_scope("ruby"):
                self.generate_implied_end_tags()
                if self.current_node().type not in ["rtc", "ruby"]:
                    self.parse_error()
            self.insert_html_element(token)

        elif is_start_tag and tag_name == "math":
            raise NotImplementedError

        elif is_start_tag and tag_name == "svg":
            raise NotImplementedError

        elif is_start_tag and tag_name in ["caption", "col", "colgroup", "frame", "head", "tbody", "td", "tfoot", "th",
                                           "thead", "tr"]:
            self.parse_error()
            return  # ignore

        else:
            self.reconstruct_active_formatting_elements()
            self.insert_html_element(token)

    def text_mode(self):
        token = self.token_stream.next()

        if token.type == "character":
            self.insert_character(token.data)

        if token.type == "EOF":
            self.parse_error()

            if self.current_node().tag_name == "script":
                raise NotImplementedError

            self.stack_of_open_elems.pop()
            self.token_stream.reprocessing = True
            self.insertion_mode = self.original_insertion_mode

        elif token.type == "end tag" and token.tag_name == "script":
            raise NotImplementedError

        else:
            self.stack_of_open_elems.pop()
            self.insertion_mode = self.original_insertion_mode
