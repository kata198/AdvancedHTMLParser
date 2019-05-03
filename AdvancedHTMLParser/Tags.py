'''
    Copyright (c) 2015, 2016, 2017, 2018, 2019 Tim Savannah under LGPLv3. All Rights Reserved.

    See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.


    AdvancedTag and TagCollection, which represent tags and their data, and other related functions.
'''

from collections import OrderedDict

import copy
import re
import uuid

from .conversions import convertBooleanStringToBoolean

from .constants import ( PREFORMATTED_TAGS, IMPLICIT_SELF_CLOSING_TAGS, TAG_NAMES_TO_ADDITIONAL_ATTRIBUTES,
    COMMON_JAVASCRIPT_ATTRIBUTES, ALL_JAVASCRIPT_EVENT_ATTRIBUTES, TAG_ITEM_BINARY_ATTRIBUTES,
    TAG_ITEM_ATTRIBUTE_LINKS, TAG_ITEM_ATTRIBUTES_SPECIAL_VALUES, TAG_ITEM_CHANGE_NAME_FROM_ATTR,
    TAG_ITEM_CHANGE_NAME_FROM_ITEM, TAG_ITEM_BINARY_ATTRIBUTES_STRING_ATTR, TAG_ITEM_ATTRIBUTES_SPECIAL_VALIDATION,
)

from .SpecialAttributes import SpecialAttributesDict, StyleAttribute, AttributeNodeMap, DOMTokenList

from .utils import escapeQuotes, tostr, stripWordsOnly

__all__ = ('AdvancedTag', 'uniqueTags', 'TagCollection', 'FilterableTagCollection', 'toggleAttributesDOM', 'isTextNode', \
    'isTagNode', 'isValidAttributeName', \
)


def isTextNode(node):
    '''
        isTextNode - Test if given node is a text node (Not a tag)

        @param node - Node to test

        @return bool
    '''
    return not issubclass(node.__class__, AdvancedTag)

def isTagNode(node):
    '''
        isTagNode - Test if given node is a tag node (AdvancedTag)

        @param node - Node to test

        @return bool
    '''
    return issubclass(node.__class__, AdvancedTag)


def isValidAttributeName(attrName):
    '''
        isValidAttributeName - Validate that an attribute name is valid.

          AdvancedHTMLParser will silently drop invalid attributes,
            ValidatingHTMLParser will raise exception

            @param attrName <str> - The attribute name to test


            @return <bool> - True if is valid name, otherwise False
    '''
    # Attribute name must start with an alpha or underscore
    if not attrName or ( not attrName[0].isalpha() and attrName[0] != '_' ):
        return False

    for thisCh in attrName:

        if thisCh.isalnum():
            # Alpha and numerics are supported
            continue

        elif thisCh in ('-', '_'):
            # Dash and underscore are allowed
            continue

        # All others are invalid
        return False

    # Validation passed
    return True





def uniqueTags(tagList):
    '''
        uniqueTags - Returns the unique tags in tagList.

            @param tagList list<AdvancedTag> : A list of tag objects.
    '''
    ret = []
    alreadyAdded = set()
    for tag in tagList:
        myUid = tag.getUid()
        if myUid in alreadyAdded:
            continue
        ret.append(tag)
    return TagCollection(ret) # Convert to a TagCollection here for performance reasons.

def toggleAttributesDOM(isEnabled):
    '''
        toggleAttributesDOM - Toggle if the old DOM tag.attributes NamedNodeMap model should be used for the .attributes method, versus

           a more sane direct dict implementation.

            The DOM version is always accessable as AdvancedTag.attributesDOM
            The dict version is always accessable as AdvancedTag.attributesDict

            Default for AdvancedTag.attributes is to be attributesDict implementation.

          @param isEnabled <bool> - If True, .attributes will be changed to use the DOM-provider. Otherwise, it will use the dict provider.
    '''

    if isEnabled:
        AdvancedTag.attributes = AdvancedTag.attributesDOM
    else:
        AdvancedTag.attributes = AdvancedTag.attributesDict

# ADVANCED_TAG_RAW_ATTRIBUTES - These are tags which are just raw attributes on AdvancedTag
#   Used to optimize access
ADVANCED_TAG_RAW_ATTRIBUTES = set( ['tagName', '_attributes', 'text', 'blocks', '_classNames', 'isSelfClosing',
                                    'children', 'parentNode', 'ownerDocument', 'uid', '_indent']
)

class AdvancedTag(object):
    '''
        AdvancedTag - Represents a Tag. Used with AdvancedHTMLParser to create a DOM-model

        Keep tag names lowercase.

        Use the getters and setters instead of attributes directly, or you may lose accounting.
    '''


    def __init__(self, tagName, attrList=None, isSelfClosing=False, ownerDocument=None):
        '''
            __init__ - Construct

                @param tagName - String of tag name. This will be lowercased!
                @param attrList - A list of tuples (key, value)
                @param isSelfClosing - True if self-closing tag ( <tagName attrs /> ) will be set to False if text or children are added.
                @param ownerDocument <None/AdvancedHTMLParser> - The parser (document) associated with this tag, or None for no association
        '''
        self.tagName = tagName.lower()

        # Using this rawSet instead of __setattr__ (which is almost always an external-only interface)
        #   greatly increases performance
        rawSet = self.__rawSet

        if isSelfClosing is False and tagName in IMPLICIT_SELF_CLOSING_TAGS:
            isSelfClosing = True


        # Directly assign these attributes without running through the
        #   public __setattr__ code
        rawSet('_attributes', SpecialAttributesDict(self))

        # TODO: Can probably just use a cached / invalidated model for 'text' instead of a distinct property.
        #         This could improve performance and memory usage both
        rawSet('text', '')

        rawSet('blocks', [''])

        # TODO: Maybe can refactor "children" into just being the "tagBlocks" from above?
        rawSet('children', [])

        rawSet('_classNames', [])
        rawSet('isSelfClosing', isSelfClosing)
        rawSet('parentNode', None)
        rawSet('ownerDocument', ownerDocument)
        rawSet('uid', uuid.uuid4())

        rawSet('_indent', '')

        # Set up "style" attribute with special interactions
        styleAttr = StyleAttribute('', self)
        rawSet('style', styleAttr)

        # If provided with a list of attributes as tuple(name, value)
        #   then apply those.
        if attrList:
            myAttributes = self._attributes

            for key, value in attrList:
                key = key.lower()

                if not isValidAttributeName(key):
                    # Silently drop this invalid key -- symbol out of place, etc.
                    continue

                myAttributes[key] = value


    def __setattr__(self, name, value):
        '''
            __setattr__ - Called with dot-access assignment, like:  myTag.attr = "value"

                This method applies the special HTML/JS rules to dot-access,
                  and allows setting several attributes directly, and conversion on special names
                  such as myTag.className -> "class" attribute

                @param name <str> - The name of the attribute after the dot

                @param value <multiple types> - The value to assign

                @return - The value assigned ( may not match the passed in #value, for example the attribute
                             "style" takes a string value, but will return a special type StyleAttribute to support
                             access with javascript-like behaviour
        '''

        # These are direct properties on the object itself, and maybe only have meaning as AdvancedHTMLParser-specific
        #   properties.
        #  NOTE: Investigate if we should intercept "classNames" here to modify "class" and "classList"
        #         (Probably will remain as-is, as it is not a standard property but specific to AdvancedHTMLParser
        if name in ADVANCED_TAG_RAW_ATTRIBUTES:
            return object.__setattr__(self, name, value)

        # Check for special "className"
        if name == "className":
            value = stripWordsOnly( tostr(value) )
            object.__setattr__(self, '_classNames', [x for x in value.split(' ') if x])
            return value

        # Check if this is one of the special items which map directly to attributes
        #    TAG_ITEM_ATTRIBUTE_LINKS - These attributes link directly to an html attribute, e.x. "id" or "name"
        #    TAG_NAMES_TO_ADDITIONAL_ATTRIBUTES - This is a map for specific dot-access attributes specific to
        #                                           a tag name. For example, javascript events or for an anchor
        #                                           the "href" or "target" attributes
        if name in TAG_ITEM_ATTRIBUTE_LINKS \
               or \
             name in TAG_NAMES_TO_ADDITIONAL_ATTRIBUTES.get(self.tagName, []):

            # Check if we have special validation on this attribute, and run it (will raise exception if invalid)
            if name in TAG_ITEM_ATTRIBUTES_SPECIAL_VALIDATION:
                TAG_ITEM_ATTRIBUTES_SPECIAL_VALIDATION[name](self, value)

            # Check if we need to adjust the name fpr setting this html attribute -
            #   these javascript names differ from the html attribute name, e.x.  "className" -> "class"
            if name in TAG_ITEM_CHANGE_NAME_FROM_ITEM:
                name = TAG_ITEM_CHANGE_NAME_FROM_ITEM[name]

            if name in TAG_ITEM_BINARY_ATTRIBUTES_STRING_ATTR:
                # NOTE: These are binary attributes, but have a string representation within html (e.x. spellcheck)
                #         Handle the value conversion etc. within the SpecialAttributesDict
                self.setAttribute(name, value)

                # Return the converted attribute
                return self.getAttribute(name)
            # Check if the value needs to be converted to a binary/boolean, e.x. "checked"
            elif name in TAG_ITEM_BINARY_ATTRIBUTES:
                # If it is a boolean html attribute, it is denoted by the presence of the field at all (any value means "True"/set/yes)
                if bool(value) is False:
                    # False, so remove attribute
                    self.removeAttribute(name)
                else:
                    # True, so ensure attribute is present
                    self.setAttribute(name, "")
                return value

            # Just a plain ol' direct mapping of js name -> html attribute name
            self.setAttribute(name, tostr(value))
            return value

        # Check if we are setting the "style" attribute, and if so,
        #   either convert a string ( e.x. "float: left; display: block" ) into a StyleAttribute object,
        #   or if already a StyleAttribute object, make a copy (e.x.  tag2.style = tag1.style )
        #
        if name == 'style':

            # Check that we aren't trying to assign our own style to ourself to prevent
            #   a copy when we shouldn't and other bad stuff
            if id(value) != id(self.style):
                # This will perform a copy if we have a StyleAttribute already, else
                #   convert a style string to a StyleAttribute object
                value = StyleAttribute(value, self)

                # Disassociate the old StyleAttribute from this tag
                oldStyle = self.__rawGet('style')
                if issubclass(oldStyle.__class__, StyleAttribute):
                    oldStyle.setTag(None)

            ret = object.__setattr__(self, 'style', value)

            # Adjust the presence of the style="..." in the html attributes
            self.style._ensureHtmlAttribute()

            return ret

        try:
            return object.__setattr__(self, name,  value)
        except AttributeError:
            raise AttributeError('Cannot set property %s. Use setAttribute?' %(name,))

    def __getattribute__(self, name):

#        if name == 'tagName':
#            return object.__getattribute__(self, 'tagName')

        # Short-circuit for performance
        try:
            return object.__getattribute__(self, name)
        except:
            pass

        # Check if this is one of the special items which map directly to attributes
        #    TAG_ITEM_ATTRIBUTE_LINKS - These attributes link directly to an html attribute, e.x. "id" or "name"
        #    TAG_NAMES_TO_ADDITIONAL_ATTRIBUTES - This is a map for specific dot-access attributes specific to
        #                                           a tag name. For example, javascript events or for an anchor
        #                                           the "href" or "target" attributes
        if name in TAG_ITEM_ATTRIBUTE_LINKS \
              or \
            name in TAG_NAMES_TO_ADDITIONAL_ATTRIBUTES.get(self.tagName, []):

            # See if this attribute has a "special" representation, TAG_ITEM_ATTRIBUTES_SPECIAL_VALUES
            #   For example, tabIndex returns "-1" if not set rather than the standard empty string
            if name in TAG_ITEM_ATTRIBUTES_SPECIAL_VALUES:
                return TAG_ITEM_ATTRIBUTES_SPECIAL_VALUES[name](self)

            # Check if given attribute has a different name via dot-access and actual attribute ( e.x. "className" -> "class" )
            #   TODO
            if name in TAG_ITEM_CHANGE_NAME_FROM_ITEM:
                name = TAG_ITEM_CHANGE_NAME_FROM_ITEM[name]

            # These have a binary representation in dot-access (this method), but a string value as an attribute.
            if name in TAG_ITEM_BINARY_ATTRIBUTES_STRING_ATTR:
                return convertBooleanStringToBoolean( self.getAttribute(name) )

            # Check if this is a binary/boolean attribute, i.e. the value is always either True or False ( e.x. "checked" )
            elif name in TAG_ITEM_BINARY_ATTRIBUTES:
                val = self.getAttribute(name, False)
                if val is not False:
                    return True

                return False

            # Javascript attributes ( e.x. "onclick" ) have a default ( i.e. unset ) value of null rather than other html attributes
            #   which default to empty string
            if name in ALL_JAVASCRIPT_EVENT_ATTRIBUTES:
                default = None
            else:
                default = ''

            # Pull attribute value off the attribute dict
            return self.getAttribute(name, default)

        # Access is not for a known attribute name. So try to pull directly off this object,
        #   or return None.
        # TODO: Since we start this method with this same call, we already know at this point
        #        the attribute is not present. So should we just return None here instead of trying again?
        try:
            return object.__getattribute__(self, name)
        except AttributeError:
            # Ensure any access that is a "miss" returns None (null/undefined)
            return None

    def __rawGet(self, name):
        '''
            __rawGet - INTERNAL - Directly get an attribute on this object without running through
                        the public interface of AdvancedTag.__getattribute__

                  @param name <str> - The attribute name to attempt to fetch

                  @return - The value of the attribute on this object denoted by #name


                  @raises - AttributeError if no such attribute is found on this object
        '''
        return object.__getattribute__(self, name)

    def __rawSet(self, name, value):
        '''
            __rawSet - INTERNAL - Directly set an attribute on this object without running through
                        the public interface of AdvancedTag.__setattr__


                  @param name <str> - The attribute name to set

                  @param value - The value to assign to #name on this object

        '''
        return object.__setattr__(self, name, value)


    def cloneNode(self):
        '''
            cloneNode - Clone this node (tag name and attributes). Does not clone children.

            Tags will be equal according to isTagEqual method, but will contain a different internal
            unique id such tag origTag != origTag.cloneNode() , as is the case in JS DOM.
        '''
        return self.__class__(self.tagName, self.getAttributesList(), self.isSelfClosing)

    def __getstate__(self):
        '''
            __getstate__ - Get state for pickling

                @return <dict>
        '''
        state = dict()

        getSelfAttr = lambda key : object.__getattribute__(self, key)

        state['tagName'] = getSelfAttr('tagName')
        state['attributesList'] = getSelfAttr('getAttributesList')()
        state['isSelfClosing'] = getSelfAttr('isSelfClosing')
        state['uid'] = getSelfAttr('uid')
        state['ownerDocument'] = getSelfAttr('ownerDocument')

        # "blocks" attribute covers both text and children
        state['blocks'] = getSelfAttr('blocks')

        return state


    def __setstate__(self, state):
        '''
            __setstate__ - Set state when loading pickle

                @param state <dict>
        '''
        # Call init on newly unpickled object to ensure everything is set properly
        __init__ = object.__getattribute__(AdvancedTag, '__init__')
        __init__(self, tagName=state['tagName'], attrList=state['attributesList'], isSelfClosing=state['isSelfClosing'])

        # Copy the uid onto this object
        self.uid = state['uid']

        # Set the ownerDocument
        self.ownerDocument = state['ownerDocument']

        # Clear current blocks, so that we don't end up with multiple of the initial,
        #   empty-string block used for indents
        self.blocks = []

        # Append children
        for block in state['blocks']:
            self.appendBlock(block)


        #myAttributes = object.__getattribute__(self, '_attributes')

        #for key, value in state['attributesList']:
        #    if key == 'style':
        ##        self.style = value
        #    elif key == 'class':
        #        self.className = value
        #    else:
        #        myAttributes._direct_set(key, value)


    def appendText(self, text):
        '''
            appendText - append some inner text
        '''
        # self.text is just raw string of the text
        self.text += text
        self.isSelfClosing = False # inner text means it can't self close anymo
        # self.blocks is either text or tags, in order of appearance
        self.blocks.append(text)


    def removeText(self, text):
        '''
            removeText - Removes the first occurace of given text in a text node (i.e. not part of a tag)

            @param text <str> - text to remove

            @return text <str/None> - The text in that block (text node) after remove, or None if not found

            NOTE: To remove a node, @see removeChild
            NOTE: To remove a block (maybe a node, maybe text), @see removeBlock
            NOTE: To remove ALL occuraces of text, @see removeTextAll
        '''
        # TODO: This would be a good candidate for the refactor of text blocks
        removedBlock = None

        # Scan all text blocks for "text"
        blocks = self.blocks
        for i in range(len(blocks)):
            block = blocks[i]

            # We only care about text blocks
            if issubclass(block.__class__, AdvancedTag):
                continue

            if text in block:
                # We have a block that matches.

                # Create a copy of the old text in this block for return
                removedBlock = block[:]
                # Remove first occurance of #text from matched block
                blocks[i] = block.replace(text, '')
                break # remove should only remove FIRST occurace, per other methods

        # Regenerate the "text" property
        self.text = ''.join([thisBlock for thisBlock in blocks if not issubclass(thisBlock.__class__, AdvancedTag)])

        # Return None if no match, otherwise the text previously within the block we removed #text from
        return removedBlock


    def removeTextAll(self, text):
        '''
            removeTextAll - Removes ALL occuraces of given text in a text node (i.e. not part of a tag)

            @param text <str> - text to remove

            @return list <str> - All text node containing #text BEFORE the text was removed.
                Empty list if no text removed

            NOTE: To remove a node, @see removeChild
            NOTE: To remove a block (maybe a node, maybe text), @see removeBlock
            NOTE: To remove a single occurace of text, @see removeText
        '''
        # TODO: This would be a good candidate for the refactor of text blocks
        removedBlocks = []

        blocks = self.blocks
        for i in range(len(blocks)):

            block = blocks[i]

            # We only care about text blocks
            if issubclass(block.__class__, AdvancedTag):
                continue

            if text in block:
                # Got a match, save a copy of the text block pre-replace for the return
                removedBlocks.append( block[:] )

                # And replace the text within this matched block
                blocks[i] = block.replace(text, '')


        # Regenerate self.text
        self.text = ''.join([thisBlock for thisBlock in blocks if not issubclass(thisBlock.__class__, AdvancedTag)])

        return removedBlocks


    def remove(self):
        '''
            remove - Will remove this node from its parent, if it has a parent (thus taking it out of the HTML tree)

                NOTE: If you are using an IndexedAdvancedHTMLParser, calling this will NOT update the index. You MUST call
                  reindex method manually.

            @return <bool> - While JS DOM defines no return for this function, this function will return True if a
               remove did happen, or False if no parent was set.
        '''
        if self.parentNode:
            self.parentNode.removeChild(self)
            # self.parentNode will now be None by 'removeChild' method
            return True
        return False


    def removeBlocks(self, blocks):
        '''
            removeBlock - Removes a list of blocks (the first occurance of each) from the direct children of this node.

            @param blocks  list<str/AdvancedTag> - List of AdvancedTags for tag nodes, else strings for text nodes

            @return The removed blocks in each slot, or None if None removed.

            @see removeChild
            @see removeText

            For multiple, @see removeBlocks
        '''
        ret = []
        for block in blocks:
            if issubclass(block.__class__, AdvancedTag):
                ret.append( self.removeChild(block) )
            else:
                # TODO: Should this just forward to removeText?
                ret.append( self.removeBlock(block) )

        return ret

    def appendChild(self, child):
        '''
            appendChild - Append a child to this element.

            @param child <AdvancedTag> - Append a child element to this element
        '''
        if child is None:
            raise KeyError('appendChild passed non-element')

        # Associate parentNode of #child to this tag
        child.parentNode = self

        # Associate owner document to child and all children recursive
        ownerDocument = self.ownerDocument

        child.ownerDocument = ownerDocument
        for subChild in child.getAllChildNodes():
            subChild.ownerDocument = ownerDocument

        # Our tag cannot be self-closing if we have a child tag
        self.isSelfClosing = False

        # Append to both "children" and "blocks"
        self.children.append(child)
        self.blocks.append(child)
        return child

    # appendNode - alias of appendChild
    appendNode = appendChild


    def appendBlock(self, block):
        '''
            append / appendBlock - Append a block to this element. A block can be a string (text node), or an AdvancedTag (tag node)

            @param <str/AdvancedTag> - block to add

            @return - #block

            NOTE: To add multiple blocks, @see appendBlocks
                  If you know the type, use either @see appendChild for tags or @see appendText for text
        '''
        # Determine block type and call appropriate method
        if isinstance(block, AdvancedTag):
            self.appendNode(block)
        else:
            self.appendText(block)

        return block

    # append - Alias (official API name) for appendBlock
    append = appendBlock


    def appendBlocks(self, blocks):
        '''
            appendBlocks - Append blocks to this element. A block can be a string (text node), or an AdvancedTag (tag node)

            @param blocks list<str/AdvancedTag> - A list, in order to append, of blocks to add.

            @return - #blocks

            NOTE: To add a single block, @see appendBlock
                  If you know the type, use either @see appendChild for tags or @see appendText for text
        '''
        for block in blocks:
            if isinstance(block, AdvancedTag):
                self.appendNode(block)
            else:
                self.appendText(block)

        return blocks


    def appendInnerHTML(self, html):
        '''
            appendInnerHTML - Appends nodes from arbitrary HTML as if doing element.innerHTML += 'someHTML' in javascript.

            @param html <str> - Some HTML

            NOTE: If associated with a document ( AdvancedHTMLParser ), the html will use the encoding associated with
                    that document.

            @return - None. A browser would return innerHTML, but that's somewhat expensive on a high-level node.
              So just call .innerHTML explicitly if you need that
        '''

        # Late-binding to prevent circular import
        from .Parser import AdvancedHTMLParser

        # Inherit encoding from the associated document, if any.
        encoding = None
        if self.ownerDocument:
            encoding = self.ownerDocument.encoding

        # Generate blocks (text nodes and AdvancedTag's) from HTML
        blocks = AdvancedHTMLParser.createBlocksFromHTML(html, encoding)

        # Throw them onto this node
        self.appendBlocks(blocks)


    def removeChild(self, child):
        '''
            removeChild - Remove a child tag, if present.

                @param child <AdvancedTag> - The child to remove

                @return - The child [with parentNode cleared] if removed, otherwise None.

                NOTE: This removes a tag. If removing a text block, use #removeText function.
                  If you need to remove an arbitrary block (text or AdvancedTag), @see removeBlock

                Removing multiple children? @see removeChildren
        '''
        try:
            # Remove from children and blocks
            self.children.remove(child)
            self.blocks.remove(child)

            # Clear parent node association on child
            child.parentNode = None

            # Clear document reference on removed child and all children thereof
            child.ownerDocument = None
            for subChild in child.getAllChildNodes():
                subChild.ownerDocument = None
            return child
        except ValueError:
            # TODO: What circumstances cause this to be raised? Is it okay to have a partial remove?
            #
            #  Is it only when "child" is not found? Should that just be explicitly tested?
            return None

    # removeNode - Alias of removeChild
    removeNode = removeChild

    def removeChildren(self, children):
        '''
            removeChildren - Remove multiple child AdvancedTags.

            @see removeChild

            @return list<AdvancedTag/None> - A list of all tags removed in same order as passed.
                Item is "None" if it was not attached to this node, and thus was not removed.
        '''
        ret = []

        for child in children:
            ret.append( self.removeChild(child) )

        return ret


    def removeBlock(self, block):
        '''
            removeBlock - Removes a single block (text node or AdvancedTag) which is a child of this object.

            @param block <str/AdvancedTag> - The block (text node or AdvancedTag) to remove.

            @return Returns the removed block if one was removed, or None if requested block is not a child of this node.

            NOTE: If you know you are going to remove an AdvancedTag, @see removeChild
                  If you know you are going to remove a text node,    @see removeText

            If removing multiple blocks, @see removeBlocks
        '''
        if issubclass(block.__class__, AdvancedTag):
            return self.removeChild(block)
        else:
            return self.removeText(block)



    def insertBefore(self, child, beforeChild):
        '''
            insertBefore - Inserts a child before #beforeChild


                @param child <AdvancedTag/str> - Child block to insert

                @param beforeChild <AdvancedTag/str> - Child block to insert before. if None, will  be appended

            @return - The added child. Note, if it is a text block (str), the return isl NOT be linked by reference.

            @raises ValueError - If #beforeChild is defined and is not a child of this node

        '''
        # When the second arg is null/None, the node is appended. The argument is required per JS API, but null is acceptable..
        if beforeChild is None:
            return self.appendBlock(child)

        # If #child is an AdvancedTag, we need to add it to both blocks and children.
        isChildTag = isTagNode(child)

        myBlocks = self.blocks
        myChildren = self.children

        # Find the index #beforeChild falls under current element
        try:
            blocksIdx =  myBlocks.index(beforeChild)
            if isChildTag:
                childrenIdx = myChildren.index(beforeChild)
        except ValueError:
            # #beforeChild is not a child of this element. Raise error.
            raise ValueError('Provided "beforeChild" is not a child of element, cannot insert.')

        # Add to blocks in the right spot
        self.blocks = myBlocks[:blocksIdx] + [child] + myBlocks[blocksIdx:]
        # Add to child in the right spot
        if isChildTag:
            self.children = myChildren[:childrenIdx] + [child] + myChildren[childrenIdx:]

        return child

    def insertAfter(self, child, afterChild):
        '''
            insertAfter - Inserts a child after #afterChild


                @param child <AdvancedTag/str> - Child block to insert

                @param afterChild <AdvancedTag/str> - Child block to insert after. if None, will  be appended

            @return - The added child. Note, if it is a text block (str), the return isl NOT be linked by reference.
        '''

        # If after child is null/None, just append
        if afterChild is None:
            return self.appendBlock(child)

        isChildTag = isTagNode(child)

        myBlocks = self.blocks
        myChildren = self.children

        # Determine where we need to insert this both in "blocks" and, if a tag, "children"
        try:
            blocksIdx =  myBlocks.index(afterChild)
            if isChildTag:
                childrenIdx = myChildren.index(afterChild)
        except ValueError:
            raise ValueError('Provided "afterChild" is not a child of element, cannot insert.')

        # Append child to requested spot
        self.blocks = myBlocks[:blocksIdx+1] + [child] + myBlocks[blocksIdx+1:]
        if isChildTag:
            self.children = myChildren[:childrenIdx+1] + [child] + myChildren[childrenIdx+1:]

        return child


    # Maybe we want to do a more full implementation of the Node stuff.... but I don't think anyone really
    #   uses this stuff
    @property
    def nodeName(self):
        '''
            nodeName - Return the name of this name (tag name)
        '''
        return self.tagName

    @property
    def nodeValue(self):
        '''
            nodeValue - Return the value of this node (None)
        '''
        return None

    @property
    def nodeType(self):
        '''
            nodeType - Return the type of this node (1 - ELEMENT_NODE)
        '''
        return 1

    @property
    def attributesDOM(self):
        '''
            attributes - Return a NamedNodeMap of the attributes on this object.

              This is a horrible method and is not used in practice anywhere sane.

              Please use setAttribute, getAttribute, hasAttribute methods instead.

              @see SpecialAttributes.NamedNodeMap

              This is NOT the default provider of the "attributes" property. Can be toggled to use the DOM-matching version, see @toggleAttributesDOM

            @return AttributeNodeMap
        '''
        return AttributeNodeMap(self._attributes, self, ownerDocument=self.ownerDocument)

    @property
    def attributesDict(self):
        '''
            attributesDict - Returns the internal dict mapped to attributes on this object.

              Modifications made here WILL affect this tag, use getAttributesDict to get a copy.

              This is the default provider of the "attributes" property. Can be toggled to use the DOM-matching version, see @toggleAttributesDOM

              @return <dict> - Internal attributes
        '''
        return self._attributes

    # attributes - Alias of "attributesDict" property.
    #                Can be changed to "attributesDOM" for a less-useful but more-strict adherance to JS API
    attributes = attributesDict

    @property
    def attributesList(self):
        '''
            attributesList - Returns a copy of internal attributes as a list. Same as getAttributesList method.

                @return list<tuple> - List of (key, value) tuples representing each attribute on this node


              @see getAttributesList
              @see attributesDict
        '''
        return self.getAttributesList()


    @property
    def firstChild(self):
        '''
            firstChild - property, Get the first child block, text or tag.

                @return <str/AdvancedTag/None> - The first child block, or None if no child blocks
        '''
        blocks = object.__getattribute__(self, 'blocks')
        # First block is empty string for indent, but don't hardcode incase that changes
        if blocks[0] == '':
           firstIdx = 1
        else:
           firstIdx = 0

        if len(blocks) == firstIdx:
            # No first child
            return None

        return blocks[1]


    @property
    def firstElementChild(self):
        '''
            firstElementChild - property, Get the first child which is an element (AdvancedTag)

                @return <AdvancedTag/None> - The first element child, or None if no element child nodes
        '''
        children = object.__getattribute__(self, 'children')

        if len(children) == 0:
            return None
        return children[0]


    @property
    def lastChild(self):
        '''
            lastChild - property, Get the last child block, text or tag

                @return <str/AdvancedTag/None> - The last child block, or None if no child blocks
        '''
        blocks = object.__getattribute__(self, 'blocks')
        # First block is empty string for indent, but don't hardcode incase that changes
        if blocks[0] == '':
           firstIdx = 1
        else:
           firstIdx = 0

        if len(blocks) <= firstIdx:
            return None

        return blocks[-1]


    @property
    def lastElementChild(self):
        '''
            lastElementChild - property, Get the last child which is an element (AdvancedTag)

                @return <AdvancedTag/None> - The last element child, or None if no element child nodes
        '''
        children = object.__getattribute__(self, 'children')

        if len(children) == 0:
            return None
        return children[-1]


    @property
    def nextSibling(self):
        '''
            nextSibling - Returns the next sibling. This is the child following this node in the parent's list of children.

                    This could be text or an element. use nextSiblingElement to ensure element

                @return <None/str/AdvancedTag> - None if there are no nodes (text or tag) in the parent after this node,
                                                    Otherwise the following node (text or tag)
        '''
        parentNode = self.parentNode

        # If no parent, no siblings.
        if not parentNode:
            return None

        # Determine index in blocks
        myBlockIdx = parentNode.blocks.index(self)

        # If we are the last, no next sibling
        if myBlockIdx == len(parentNode.blocks) - 1:
            return None

        # Else, return the next block in parent
        return parentNode.blocks[ myBlockIdx + 1 ]

    @property
    def nextElementSibling(self):
        '''
            nextElementSibling - Returns the next sibling that is an element.
                This is the tag node following this node in the parent's list of children

                @return <None/AdvancedTag> - None if there are no children (tag) in the parent after this node,
                                                    Otherwise the following element (tag)
        '''
        parentNode = self.parentNode

        # If no parent, no siblings
        if not parentNode:
            return None

        # Determine the index in children
        myElementIdx = parentNode.children.index(self)

        # If we are last child, no next sibling
        if myElementIdx == len(parentNode.children) - 1:
            return None

        # Else, return the next child in parent
        return parentNode.children[myElementIdx+1]

    nextSiblingElement = nextElementSibling

    @property
    def previousSibling(self):
        '''
            previousSibling - Returns the previous sibling. This would be the previous node (text or tag) in the parent's list

                This could be text or an element. use previousSiblingElement to ensure element


                @return <None/str/AdvancedTag> - None if there are no nodes (text or tag) in the parent before this node,
                                                    Otherwise the previous node (text or tag)
        '''
        parentNode = self.parentNode

        # If no parent, no previous sibling
        if not parentNode:
            return None

        # Determine block index on parent of this node
        myBlockIdx = parentNode.blocks.index(self)

        # If we are the first, no previous sibling
        if myBlockIdx == 0:
            return None

        # Else, return the previous block in parent
        return parentNode.blocks[myBlockIdx-1]

    @property
    def previousElementSibling(self):
        '''
            previousElementSibling - Returns the previous  sibling  that is an element.

                                        This is the previous tag node in the parent's list of children


                @return <None/AdvancedTag> - None if there are no children (tag) in the parent before this node,
                                                    Otherwise the previous element (tag)

        '''
        parentNode = self.parentNode

        # If no parent, no siblings
        if not parentNode:
            return None

        # Determine this node's index in the children of parent
        myElementIdx = parentNode.children.index(self)

        # If we are the first child, no previous element
        if myElementIdx == 0:
            return None

        # Else, return previous element tag
        return parentNode.children[myElementIdx-1]

    previousSiblingElement = previousElementSibling


    @property
    def tagBlocks(self):
        '''
            tagBlocks - Property.
                        Returns all the blocks which are direct children of this node, where that block is a tag (not text)

                NOTE: This is similar to .children , and you should probably use .children instead except within this class itself

                @return list<AdvancedTag> - A list of direct children which are tags.
        '''
        myBlocks = self.blocks

        return [block for block in myBlocks if issubclass(block.__class__, AdvancedTag)]


    def getBlocksTags(self):
        '''
            getBlocksTags - Returns a list of tuples referencing the blocks which are direct children of this node, and the block is an AdvancedTag.

                The tuples are ( block, blockIdx ) where "blockIdx" is the index of self.blocks wherein the tag resides.

                @return list< tuple(block, blockIdx) > - A list of tuples of child blocks which are tags and their index in the self.blocks list
        '''
        myBlocks = self.blocks

        return [ (myBlocks[i], i) for i in range( len(myBlocks) ) if issubclass(myBlocks[i].__class__, AdvancedTag) ]


    @property
    def textBlocks(self):
        '''
            textBlocks - Property.
                        Returns all the blocks which are direct children of this node, where that block is a text (not a tag)

                @return list<AdvancedTag> - A list of direct children which are text.
        '''
        myBlocks = self.blocks

        return [block for block in myBlocks if not issubclass(block.__class__, AdvancedTag)]

    @property
    def innerText(self):
        '''
            innerText - property, gets the text of just this node. Use #textContent for this node and all children

                    This is an alias of the .text property

                 @return <str> - The text of this node
        '''
        return self.text


    @property
    def textContent(self):
        '''
            textContent - property, gets the text of this node and all inner nodes.

                Use .innerText for just this node's text

              @return <str> - The text of all nodes at this level or lower
        '''

        def _collateText(curNode):
            '''
                _collateText - Recursive function to gather the "text" of all blocks

                                 in the order that they appear

                    @param curNode <AdvancedTag> - The current AdvancedTag to process

                    @return list<str> - A list of strings in order. Join using '' to obtain text
                                            as it would appear
            '''

            curStrLst = []
            blocks = object.__getattribute__(curNode, 'blocks')

            for block in blocks:
                if isTagNode(block):
                    curStrLst += _collateText(block)
                else:
                    curStrLst.append(block)

            return curStrLst

        return ''.join(_collateText(self))


    def getBlocksText(self):
        '''
            getBlocksText - Returns a list of tuples referencing the blocks which are direct children of this node, and the block is a text node (not an AdvancedTag)

                The tuples are ( block, blockIdx ) where "blockIdx" is the index of self.blocks wherein the text resides.

                @return list< tuple(block, blockIdx) > - A list of tuples of child blocks which are not tags and their index in the self.blocks list
        '''
        myBlocks = self.blocks

        return [ (myBlocks[i], i) for i in range( len(myBlocks) ) if not issubclass(myBlocks[i].__class__, AdvancedTag) ]


    def getChildren(self):
        '''
            getChildren - returns child nodes as a searchable TagCollection.

                For a plain list, use .children instead

                @return - TagCollection of the immediate children to this tag.
        '''
        return TagCollection(self.children)

    def hasChild(self, child):
        '''
            hasChild - Returns if #child is a DIRECT child (tag) of this node.

            @param child <AdvancedTag> - The tag to check

            @return <bool> - If #child is a direct child of this node, True. Otherwise, False.
        '''
        return bool(child in self.children)


    def hasChildNodes(self):
        '''
            hasChildNodes - Checks if this node has any children (tags).

            @return <bool> - True if this child has any children, otherwise False.
        '''
        return bool(len(self.children) != 0)


    def contains(self, other):
        '''
            contains - Check if a provided tag appears anywhere as a direct child to this node, or is this node itself.

                @param other <AdvancedTag> - Tag to check

            @return <bool> - True if #other appears anywhere beneath or is this tag, otherwise False
        '''
        return self.containsUid(other.uid)


    def containsUid(self, uid):
        '''
            containsUid - Check if the uid (unique internal ID) appears anywhere as a direct child to this node, or the node itself.

                @param uid <uuid.UUID> - uuid to check

            @return <bool> - True if #uid is this node's uid, or is the uid of any children at any level down
        '''
        # Check if this node is the match
        if self.uid == uid:
            return True

        # Scan all children
        for child in self.children:
            if child.containsUid(uid):
                return True

        return False

    def getAllChildNodes(self):
        '''
            getAllChildNodes - Gets all the children, and their children,
               and their children, and so on, all the way to the end as a TagCollection.

               Use .childNodes for a regular list

            @return TagCollection<AdvancedTag> - A TagCollection of all children (and their children recursive)
        '''

        ret = TagCollection()

        # Scan all the children of this node
        for child in self.children:
            # Append each child
            ret.append(child)

            # Append children's children recursive
            ret += child.getAllChildNodes()

        return ret

    def getAllNodes(self):
        '''
            getAllNodes - Returns this node, all children, and all their children and so on till the end

            @return TagCollection<AdvancedTag>
        '''

        # Start with a tag collection including this tag
        ret = TagCollection([self])

        # And all children, and their children recursive
        ret += self.getAllChildNodes()

        return ret


    def getAllChildNodeUids(self):
        '''
            getAllChildNodeUids - Returns all the unique internal IDs for all children, and there children,
              so on and so forth until the end.

              For performing "contains node" kind of logic, this is more efficent than copying the entire nodeset

            @return set<uuid.UUID> A set of uuid objects
        '''
        ret = set()

        # Iterate through all children
        for child in self.children:
            # Add child's uid
            ret.add(child.uid)
            # Add child's children's uid and their children, recursive
            ret.update(child.getAllChildNodeUids())

        return ret

    def getAllNodeUids(self):
        '''
            getAllNodeUids - Returns all the unique internal IDs from getAllChildNodeUids, but also includes this tag's uid

            @return set<uuid.UUID> A set of uuid objects
        '''
        # Start with a set including this tag's uuid
        ret = { self.uid }

        ret.update(self.getAllChildNodeUids())

        return ret


    def getPeers(self):
        '''
            getPeers - Get elements who share a parent with this element

            @return - TagCollection of elements
        '''
        parentNode = self.parentNode
        # If no parent, no peers
        if not parentNode:
            return None

        peers = parentNode.children

        # Otherwise, get all children of parent excluding this node
        return TagCollection([peer for peer in peers if peer is not self])


    @property
    def peers(self):
        '''
            peers - Get elements with same parent as this item

            @return - TagCollection of elements
        '''
        return self.getPeers()

    @property
    def childNodes(self):
        '''
            childNodes - returns immediate child nodes as a TagCollection

            @return - TagCollection of child nodes

            NOTE: Unlike JS DOM, this returns ONLY tags, not text blocks.
                   Changing this would be a fairly-major backwards-incompatible change,
                   and will likely be made in a future version.

                   For now, use @see childBlocks method to get both text AND tags
        '''
        return TagCollection(self.children)

    @property
    def childBlocks(self):
        '''
            childBlocks - Return immediate child blocks, both text and tags.

            @return list<AdvancedTag/str> - List of blocks associated with this node

            NOTE: This does what #childNodes does in JS DOM. Because for many years childNodes has returned
              ONLY tags on AdvancedHTMLParser, it would be a major change to match. Likely will be made in a future
              version.
        '''
        return self.blocks

    def getChildBlocks(self):
        '''
            getChildBlocks - Gets the child blocks, both text and tags.

            @see childBlocks
        '''
        return self.childBlocks

    @property
    def childElementCount(self):
        '''
            childElementCount - Returns the number of direct children to this node

            @return <int> - The number of direct children to this node
        '''
        return len(self.children)

    @property
    def parentElement(self):
        '''
            parentElement - get the parent element of this node

                @return <AdvancedTag/None> - The parent node, or None if no parent
        '''
        return self.parentNode

    @property
    def className(self):
        '''
            className - property, string of 'class' attribute

            @return <str> - Class attribute, or empty string if not set
        '''
        return str(self.classList)

    @property
    def classList(self):
        '''
            classList - get a copy of the list of the class names ( the "class" attribute ) for this element

                @return DOMTokenList<str> - A list of the class names for this element
        '''
        return DOMTokenList(self._classNames[:])

    classNames = classList

    def getUid(self):
        '''
            getUid - Get the AdvancedHTMLParser unique id for this tag.

                Each tag is given a generated uuid at create time, and copies also get their own unique identifier.

                This can be used to determine if two tags are the same tag, beyond just having equal attribute name/value pairs and children.

                This is used internally to prevent duplicates, for example a TagCollection does not allow multiple tags with the same uid

                @return - uuid.UUID object, representing a uuid as specified by RFC 4122, version 4.
                   This object is optimized for comparison. For a string representation, str() the result, or use .hex or .variant
        '''
        return self.uid

    def getTagName(self):
        '''
            getTagName - Gets the tag name of this Tag (lowercase).

            @return - str - name of tag
        '''
        return self.tagName

    def getStartTag(self):
        '''
            getStartTag - Returns the start tag represented as HTML

            @return - String of start tag with attributes
        '''
        attributeStrings = []
        # Get all attributes as a tuple (name<str>, value<str>)
        for name, val in self._attributes.items():
            # Get all attributes
            if val:
                val = tostr(val)

            # Only binary attributes have a "present/not present"
            if val or name not in TAG_ITEM_BINARY_ATTRIBUTES:
                # Escape any quotes found in the value
                val = escapeQuotes(val)

                # Add a name="value" to the resulting string
                attributeStrings.append('%s="%s"' %(name, val) )
            else:
                # This is a binary attribute, and thus only includes the name ( e.x. checked )
                attributeStrings.append(name)

        # Join together all the attributes in @attributeStrings list into a string
        if attributeStrings:
            attributeString = ' ' + ' '.join(attributeStrings)
        else:
            attributeString = ''

        # If this is a self-closing tag, generate like  <tag attr1="val" attr2="val2" />  with the close "/>"
        # Include the indent prior to tag opening
        if self.isSelfClosing is False:
            return "%s<%s%s >" %(self._indent, self.tagName, attributeString)
        else:
            return "%s<%s%s />" %(self._indent, self.tagName, attributeString)

    def getEndTag(self):
        '''
            getEndTag - returns the end tag representation as HTML string

            @return - String of end tag
        '''
        # If this is a self-closing tag, we have no end tag (opens and closes in the start)
        if self.isSelfClosing is True:
            return ''

        tagName = self.tagName

        # Do not add any indentation to the end of preformatted tags.
        if self._indent and tagName in PREFORMATTED_TAGS:
            return "</%s>" %(tagName, )

        # Otherwise, indent the end of this tag
        return "%s</%s>" %(self._indent, tagName)

    @property
    def innerHTML(self):
        '''
            innerHTML - Returns an HTML string of the inner contents of this tag, including children.

            @return - String of inner contents HTML
        '''

        # If a self-closing tag, there are no contents
        if self.isSelfClosing is True:
            return ''

        # Assemble all the blocks.
        ret = []

        # Iterate through blocks
        for block in self.blocks:
            # For each block:
            #   If a tag, append the outer html (start tag, contents, and end tag)
            #   Else, append the text node directly

            if isinstance(block, AdvancedTag):
                ret.append(block.outerHTML)
            else:
                ret.append(block)

        try:
            return ''.join(ret)
        except:
            import pdb; pdb.set_trace()
            return ''.join(ret)

    @property
    def outerHTML(self):
        '''
            outerHTML - Returns start tag, innerHTML, and end tag as HTML string

            @return - String of start tag, innerHTML, and end tag
        '''
        return self.getStartTag() + self.innerHTML + self.getEndTag()


    def getAttribute(self, attrName, defaultValue=None):
        '''
            getAttribute - Gets an attribute on this tag. Be wary using this for classname, maybe use addClass/removeClass. Attribute names are all lowercase.
                @return - The attribute value, or None if none exists.
        '''

        if attrName in TAG_ITEM_BINARY_ATTRIBUTES:
            if attrName in self._attributes:
                attrVal = self._attributes[attrName]
                if not attrVal:
                    return True # Empty valued binary attribute

                return attrVal # optionally-valued binary attribute
            else:
                return False
        else:
            return self._attributes.get(attrName, defaultValue)


    def getAttributesList(self):
        '''
            getAttributesList - Get a copy of all attributes as a list of tuples (name, value)

              ALL values are converted to string and copied, so modifications will not affect the original attributes.
                If you want types like "style" to work as before, you'll need to recreate those elements (like StyleAttribute(strValue) ).

              @return list< tuple< str(name), str(value) > > - A list of tuples of attrName, attrValue pairs, all converted to strings.

                This is suitable for passing back into AdvancedTag when creating a new tag.
        '''
        return [ (tostr(name)[:], tostr(value)[:]) for name, value in self._attributes.items() ]


    def getAttributesDict(self):
        '''
            getAttributesDict - Get a copy of all attributes as a dict map of name -> value

              ALL values are converted to string and copied, so modifications will not affect the original attributes.
                If you want types like "style" to work as before, you'll need to recreate those elements (like StyleAttribute(strValue) ).

              @return <dict ( str(name), str(value) )> - A dict of attrName to attrValue , all as strings and copies.
        '''

        return { tostr(name)[:] : tostr(value)[:] for name, value in self._attributes.items() }


    def setAttribute(self, attrName, attrValue):
        '''
            setAttribute - Sets an attribute. Be wary using this for classname, maybe use addClass/removeClass. Attribute names are all lowercase.

            @param attrName <str> - The name of the attribute

            @param attrValue <str> - The value of the attribute


            @raises -

                KeyError if #attrName is invalid name for an attribute
        '''
        if not isValidAttributeName(attrName):
            raise KeyError('Attribute name "%s" is not valid. Must start with alpha character, and contain only alphanumeric or "-" or "_".' %(attrName, ))
        self._attributes[attrName] = attrValue


    def setAttributes(self, attributesDict):
        '''
            setAttributes - Sets  several attributes at once, using a dictionary of attrName : attrValue

            @param  attributesDict - <str:str> - New attribute names -> values

            @raises -

        '''
        for attrName, attrValue in attributesDict.items():

            self.setAttribute(attrName, attrValue)


    def hasAttribute(self, attrName):
        '''
            hasAttribute - Checks for the existance of an attribute. Attribute names are all lowercase.

                @param attrName <str> - The attribute name

                @return <bool> - True or False if attribute exists by that name
        '''
        attrName = attrName.lower()

        # Check if requested attribute is present on this node
        return bool(attrName in self._attributes)

    def removeAttribute(self, attrName):
        '''
            removeAttribute - Removes an attribute, by name.

            @param attrName <str> - The attribute name

        '''
        attrName = attrName.lower()

        # Delete provided attribute name ( #attrName ) from attributes map
        try:
            del self._attributes[attrName]
        except KeyError:
            pass

    def hasClass(self, className):
        '''
            hasClass - Test if this tag has a paticular class name ( class attribute )

            @param className - A class to search

            @return <bool> - True if provided class is present, otherwise False
        '''
        return bool(className in self._classNames)


    def addClass(self, className):
        '''
            addClass - append a class name to the end of the "class" attribute, if not present

                @param className <str> - The name of the class to add
        '''
        className = stripWordsOnly(className)

        if not className:
            return None

        if ' ' in className:
            # Multiple class names passed, do one at a time
            for oneClassName in className.split(' '):
                self.addClass(oneClassName)
            return

        myClassNames = self._classNames

        # Do not allow duplicates
        if className in myClassNames:
            return

        # Regenerate "classNames" and "class" attr.
        #   TODO: Maybe those should be properties?
        myClassNames.append(className)

        return None


    def removeClass(self, className):
        '''
            removeClass - remove a class name if present. Returns the class name if  removed, otherwise None.

                @param className <str> - The name of the class to remove

                @return <str> - The class name removed if one was removed, otherwise None if #className wasn't present
        '''
        className = stripWordsOnly(className)

        if not className:
            return None

        if ' ' in className:
            # Multiple class names passed, do one at a time
            for oneClassName in className.split(' '):
                self.removeClass(oneClassName)
            return

        myClassNames = self._classNames

        # If not present, this is a no-op
        if className not in myClassNames:
            return None


        myClassNames.remove(className)

        return className


    def getStyleDict(self):
        '''
            getStyleDict - Gets a dictionary of style attribute/value pairs.

            @return - OrderedDict of "style" attribute.
        '''

        # TODO: This method is not used and does not appear in any tests.

        styleStr = (self.getAttribute('style') or '').strip()
        styles = styleStr.split(';') # Won't work for strings containing semicolon..
        styleDict = OrderedDict()
        for item in styles:
            try:
                splitIdx = item.index(':')
                name = item[:splitIdx].strip().lower()
                value = item[splitIdx+1:].strip()
                styleDict[name] = value
            except:
                continue

        return styleDict


    def getStyle(self, styleName):
        '''
            getStyle - Gets the value of a style paramater, part of the "style" attribute

            @param styleName - The name of the style

            @return - String of the value of the style. '' is no value.
        '''
        return getattr(self.style, styleName.lower())


    def setStyle(self, styleName, styleValue):
        '''
            setStyle - Sets a style param. Example: "display", "block"

                If you need to set many styles on an element, use setStyles instead.
                It takes a dictionary of attribute, value pairs and applies it all in one go (faster)

                To remove a style, set its value to empty string.
                When all styles are removed, the "style" attribute will be nullified.

            @param styleName - The name of the style element
            @param styleValue - The value of which to assign the style element

            @return - String of current value of "style" after change is made.
        '''
        myAttributes = self._attributes

        if 'style' not in myAttributes:
            myAttributes['style'] = "%s: %s" %(styleName, styleValue)
        else:
            setattr(myAttributes['style'], styleName, styleValue)
#        setattr(self.style, styleName, styleValue)

    def setStyles(self, styleUpdatesDict):
        '''
            setStyles - Sets one or more style params.
                This all happens in one shot, so it is much much faster than calling setStyle for every value.

                To remove a style, set its value to empty string.
                When all styles are removed, the "style" attribute will be nullified.

            @param styleUpdatesDict - Dictionary of attribute : value styles.

            @return - String of current value of "style" after change is made.
        '''
        setStyleMethod = self.setStyle
        for newName, newValue in styleUpdatesDict.items():
            setStyleMethod(newName, newValue)

        return self.style


    def _old__str__(self):
        '''
            _old__str__ - The old impl for __str__ (before 7.3.1) which just contains the start tag, inner text, and end tag.

                I think this can cause some unexpected results, especially with no "toHTML" methods etc.

                @return <str> - Start tag, inner text, and end tag
        '''
        return self.getStartTag() + self.text + self.getEndTag()


    def __str__(self):
        '''
            __str__ - Returns the HTML representation for this tag (including children).

                NOTE: This changed in 7.3.1 to be equivilant to self.outerHTML (or to new getHTML method, which is the same).

                The old method just included the start tag, the joined direct text node children, and the end tag.
                    This compacts well for debug display, but doesn't give a clear picture of what's going on.

                The old method is still available as AdvancedTag._old__str__

                To revert str(myTag) back to the hold behaviour:

                    from AdvancedHTMLParser.Tags import AdvancedTag

                    AdvancedTag.__str__ = AdvancedTag._old__str__
        '''
        return self.outerHTML


    def toHTML(self):
        '''
            toHTML - Get the HTML representation of this tag and all children

              @return <str> - HTML with this tag as the root
        '''
        return self.outerHTML


    # asHTML - Alias of toHTML
    asHTML = toHTML

    # getHTML - Alias of toHTML
    getHTML = toHTML


    def __getitem__(self, key):
        return self.children[key]

    def getElementById(self, _id):
        '''
            getElementById - Search children of this tag for a tag containing an id

            @param _id - String of id

            @return - AdvancedTag or None
        '''
        for child in self.children:
            if child.getAttribute('id') == _id:
                return child
            found = child.getElementById(_id)
            if found is not None:
                return found
        return None

    def getElementsByAttr(self, attrName, attrValue):
        '''
            getElementsByAttr - Search children of this tag for tags with an attribute name/value pair

            @param attrName - Attribute name (lowercase)
            @param attrValue - Attribute value

            @return - TagCollection of matching elements
        '''
        elements = []
        for child in self.children:
            if child.getAttribute(attrName) == attrValue:
                elements.append(child)
            elements += child.getElementsByAttr(attrName, attrValue)
        return TagCollection(elements)

    def getElementsByName(self, name):
        '''
            getElementsByName - Search children of this tag for tags with a given name

            @param name - name to search

            @return - TagCollection of matching elements
        '''
        return self.getElementsByAttr('name', name)

    def getElementsByClassName(self, className):
        '''
            getElementsByClassName - Search children of this tag for tags containing a given class name

            @param className - Class name

            @return - TagCollection of matching elements
        '''
        elements = []
        for child in self.children:
            if child.hasClass(className) is True:
                elements.append(child)
            elements += child.getElementsByClassName(className)
        return TagCollection(elements)

    def getElementsWithAttrValues(self, attrName, attrValues):
        '''
            getElementsWithAttrValues - Search children of this tag for tags with an attribute name and one of several values

            @param attrName <lowercase str> - Attribute name (lowercase)
            @param attrValues set<str> - set of acceptable attribute values

            @return - TagCollection of matching elements
        '''
        elements = []

        for child in self.children:
            if child.getAttribute(attrName) in attrValues:
                elements.append(child)
            elements += child.getElementsWithAttrValues(attrName, attrValues)
        return TagCollection(elements)


    def getElementsCustomFilter(self, filterFunc):
        '''
            getElementsCustomFilter - Searches children of this tag for those matching a provided user function

            @param filterFunc <function> - A function or lambda expression that should return "True" if the passed node matches criteria.

            @return - TagCollection of matching results

            @see getFirstElementCustomFilter
        '''
        elements = []

        for child in self.children:
            if filterFunc(child) is True:
                elements.append(child)
            elements += child.getElementsCustomFilter(filterFunc)

        return TagCollection(elements)

    def getFirstElementCustomFilter(self, filterFunc):
        '''
            getFirstElementCustomFilter - Gets the first element which matches a given filter func.

                Scans first child, to the bottom, then next child to the bottom, etc. Does not include "self" node.

            @param filterFunc <function> - A function or lambda expression that should return "True" if the passed node matches criteria.

            @return <AdvancedTag/None> - First match, or None

            @see getElementsCustomFilter
        '''

        for child in self.children:
            if filterFunc(child) is True:
                return child

            childSearchResult = child.getFirstElementCustomFilter(filterFunc)
            if childSearchResult is not None:
                return childSearchResult

        return None

    def getParentElementCustomFilter(self, filterFunc):
        '''
            getParentElementCustomFilter - Runs through parent on up to document root, returning the

                                              first tag which filterFunc(tag) returns True.

                @param filterFunc <function/lambda> - A function or lambda expression that should return "True" if the passed node matches criteria.

                @return <AdvancedTag/None> - First match, or None


                @see getFirstElementCustomFilter for matches against children
        '''
        parentNode = self.parentNode
        while parentNode:

            if filterFunc(parentNode) is True:
                return parentNode

            parentNode = parentNode.parentNode

        return None


    def getPeersCustomFilter(self, filterFunc):
        '''
            getPeersCustomFilter - Get elements who share a parent with this element and also pass a custom filter check

                @param filterFunc <lambda/function> - Passed in an element, and returns True if it should be treated as a match, otherwise False.

                @return <TagCollection> - Resulting peers, or None if no parent node.
        '''
        peers = self.peers
        if peers is None:
            return None

        return TagCollection([peer for peer in peers if filterFunc(peer) is True])


    def getPeersByAttr(self, attrName, attrValue):
        '''
            getPeersByAttr - Gets peers (elements on same level) which match an attribute/value combination.

            @param attrName - Name of attribute
            @param attrValue - Value that must match

            @return - None if no parent element (error condition), otherwise a TagCollection of peers that matched.
        '''
        peers = self.peers
        if peers is None:
            return None
        return TagCollection([peer for peer in peers if peer.getAttribute(attrName) == attrValue])

    def getPeersWithAttrValues(self, attrName, attrValues):
        '''
            getPeersWithAttrValues - Gets peers (elements on same level) whose attribute given by #attrName
                are in the list of possible vaues #attrValues

            @param attrName - Name of attribute
            @param attrValues - List of possible values which will match

            @return - None if no parent element (error condition), otherwise a TagCollection of peers that matched.
        '''
        peers = self.peers
        if peers is None:
            return None
        return TagCollection([peer for peer in peers if peer.getAttribute(attrName) in attrValues])

    def getPeersByName(self, name):
        '''
            getPeersByName - Gets peers (elements on same level) with a given name

            @param name - Name to match

            @return - None if no parent element (error condition), otherwise a TagCollection of peers that matched.
        '''
        peers = self.peers
        if peers is None:
            return None
        return TagCollection([peer for peer in peers if peer.name == name])

    def getPeersByClassName(self, className):
        '''
            getPeersByClassName - Gets peers (elements on same level) with a given class name

            @param className - classname must contain this name

            @return - None if no parent element (error condition), otherwise a TagCollection of peers that matched.
        '''
        peers = self.peers
        if peers is None:
            return None
        return TagCollection([peer for peer in peers if peer.hasClass(className)])

    def __repr__(self):
        '''
            __repr__ - A reconstructable representation of this AdvancedTag.

                TODO: Incorporate uid somehow? Without it the tags won't be the SAME TAG, but they'll be equivilant
        '''
        return "%s(%s, %s, %s)" %(self.__class__.__name__, repr(self.tagName), repr(self.getAttributesList()), repr(self.isSelfClosing))
#        return "%s(%s, %s, %s) # uid=%s" %(self.__class__.__name__, repr(self.tagName), repr(self.getAttributesList()), repr(self.isSelfClosing), self.uid)


    def isTagEqual(self, other):
        '''
            isTagEqual - Compare if a tag contains the same tag name and attributes as another tag,

                i.e. if everything between < and > parts of this tag are the same.

                Does NOT compare children, etc. Does NOT compare if these are the same exact tag in the html (use regular == operator for that)

                So for example:

                    tag1 = document.getElementById('something')
                    tag2 = copy.copy(tag1)

                    tag1 == tag2          # This is False
                    tag1.isTagEqual(tag2) # This is True

                @return bool - True if tags have the same name and attributes, otherwise False
        '''
#        if type(other) != type(self):
#            return False

#       NOTE: Instead of type check,
#          just see if we can get the needed attributes in case subclassing
        try:
            if self.tagName != other.tagName:
                return False

            myAttributes = self._attributes
            otherAttributes = other._attributes

            attributeKeysSelf = list(myAttributes.keys())
            attributeKeysOther = list(otherAttributes.keys())
        except:
            return False

        # Check that we have all the same attribute names
        if set(attributeKeysSelf) != set(attributeKeysOther):
            return False

        for key in attributeKeysSelf:

            if myAttributes.get(key) != otherAttributes.get(key):
                return False

        return True


    def filter(self, **kwargs):
        '''
            filter aka filterAnd - Perform a filter operation on this node and all children (and all their children, onto the end)

            Results must match ALL the filter criteria. for ANY, use the *Or methods

            For special filter keys, @see #AdvancedHTMLParser.AdvancedHTMLParser.filter

            Requires the QueryableList module to be installed (i.e. AdvancedHTMLParser was installed
              without '--no-deps' flag.)

            For alternative without QueryableList,
              consider #AdvancedHTMLParser.AdvancedHTMLParser.find method or the getElement* methods

            @return TagCollection<AdvancedTag>
        '''
        if canFilterTags is False:
            raise NotImplementedError('filter methods requires QueryableList installed, it is not. Either install QueryableList, or try the less-robust "find" method, or the getElement* methods.')

        allNodes = self.getAllNodes()

        filterableNodes = FilterableTagCollection(allNodes)

        return filterableNodes.filterAnd(**kwargs)

    filterAnd = filter

    def filterOr(self, **kwargs):
        '''
            filterOr - Perform a filter operation on this node and all children (and their children, onto the end)

            Results must match ANY the filter criteria. for ALL, use the *AND methods

            For special filter keys, @see #AdvancedHTMLParser.AdvancedHTMLParser.filter

            Requires the QueryableList module to be installed (i.e. AdvancedHTMLParser was installed
              without '--no-deps' flag.)

            For alternative without QueryableList,
              consider #AdvancedHTMLParser.AdvancedHTMLParser.find method or the getElement* methods

            @return TagCollection<AdvancedTag>
        '''
        if canFilterTags is False:
            raise NotImplementedError('filter methods requires QueryableList installed, it is not. Either install QueryableList, or try the less-robust "find" method, or the getElement* methods.')

        allNodes = self.getAllNodes()

        filterableNodes = FilterableTagCollection(allNodes)

        return filterableNodes.filterOr(**kwargs)



    def __eq__(self, other):
        '''
            __eq__ - Test if this and other are THE SAME TAG.

            Note: this does NOT test if the tags have the same name, attributes, etc.
                Use isTagEqual to test if a tag has the same data (other than children)

            So for example:

                tag1 = document.getElementById('something')
                tag2 = copy.copy(tag1)

                tag1 == tag2          # This is False
                tag1.isTagEqual(tag2) # This is True
        '''
        if type(other) != type(self):
            return False
        return self.uid == other.uid

    '''
        isEqualNode - Compares the internal ID of a node (same as == operator). A node will only equal itself.
    '''
    isEqualNode = __eq__

    def __ne__(self, other):
        '''
            __ne__ - Test if this and other are NOT THE SAME TAG. Note

            Note: this does NOT test if the tags have the same name, attributes, etc.
                Use isTagEqual to test if a tag has the same data (other than children)

            @see AdvancedTag.__eq__
            @see AdvancedTag.isTagEqual
        '''

        if type(other) != type(self):
            return True
        return self.uid != other.uid


    # Copy methods - Create exact copies (including copying uid)
    def __copy__(self):
        '''
            __copy__ - Create a copy (except uid). This tag will NOT ==.

               but is safe to add to the same tree as its original
        '''
        ret = self.__class__(self.tagName, self.getAttributesList(), self.isSelfClosing)

        return ret

    def __deepcopy__(self, arg):
        '''
            __deepcopy__ - Create a copy (except uid) for deepcopy. This tag will NOT ==

               but is safe to add to the same tree as its original
        '''
        ret = self.__class__(self.tagName, self.getAttributesList(), self.isSelfClosing)

        return ret

    def __hash__(self):
        return hash(self.uid)


class TagCollection(list):
    '''
        A collection of AdvancedTags. You may use this like a normal list, or you can use the various getElements* functions within to operate on the results.
        Generally, this is the return of all get* functions.

        All the get* functions called on a TagCollection search all contained elements and their childrens. If you need to check ONLY the elements in the tag collection, and not their children,
        either provide your own list comprehension to do so, or use the "filterCollection" method, which takes an arbitrary function/lambda expression and filters just the immediate tags.
    '''

    def __init__(self, values=None):
        '''
            Create this object.

            @param values - Initial values, or None for empty
        '''
        list.__init__(self)
        self.uids = set()
        if values is not None:
            self.__iadd__(values)

    @staticmethod
    def _subset(ret, cmpFunc, tag):
        if cmpFunc(tag) is True and ret._hasTag(tag) is False:
            ret.append(tag)

        for subtag in tag.getChildren():
            TagCollection._subset(ret, cmpFunc, subtag)

        return ret

    def __add__(self, others):
        # Maybe this can be optimized by changing self.uids to a dictionary, and using appending the set difference
        hasTag = self._hasTag

        ret = TagCollection(self[:])
        for other in others:
            if hasTag(other) is False:
                ret.append(other)
        return ret

    def __iadd__(self, others):
        hasTag = self._hasTag

        for other in others:
            if hasTag(other) is False:
                self.append(other)
        return self

        return self


    def __sub__(self, others):
        hasTag = self._hasTag

        ret = TagCollection(self[:])

        for other in others:
            if hasTag(other) is True:
                ret.remove(other)
        return ret

    def __isub__(self, others):
        hasTag = self._hasTag

        for other in others:
            if hasTag(other) is True:
                self.remove(other)
        return self


    def _hasTag(self, tag):
        return tag.uid in self.uids

    def append(self, tag):
        '''
            append - Append an item to this tag collection

            @param tag - an AdvancedTag
        '''
        list.append(self, tag)
        self.uids.add(tag.uid)

    def remove(self, toRemove):
        '''
            remove - Remove an item from this tag collection

            @param toRemove - an AdvancedTag
        '''
        list.remove(self, toRemove)
        self.uids.remove(toRemove.uid)

    def all(self):
        '''
            all - A plain list of these elements

            @return - List of these elements
        '''
        return list(self)

    def filterCollection(self, filterFunc):
        '''
            filterCollection - Filters only the immediate objects contained within this Collection against a function, not including any children

            @param filterFunc <function> - A function or lambda expression that returns True to have that element match

            @return TagCollection<AdvancedTag>
        '''
        ret = TagCollection()
        if len(self) == 0:
            return ret

        for tag in self:
            if filterFunc(tag) is True:
                ret.append(tag)

        return ret

    def getElementsByTagName(self, tagName):
        '''
            getElementsByTagName - Gets elements within this collection having a specific tag name

            @param tagName - String of tag name

            @return - TagCollection of unique elements within this collection with given tag name
        '''
        ret = TagCollection()
        if len(self) == 0:
            return ret

        tagName = tagName.lower()
        _cmpFunc = lambda tag : bool(tag.tagName == tagName)

        for tag in self:
            TagCollection._subset(ret, _cmpFunc, tag)

        return ret


    def getElementsByName(self, name):
        '''
            getElementsByName - Get elements within this collection having a specific name

            @param name - String of "name" attribute

            @return - TagCollection of unique elements within this collection with given "name"
        '''
        ret = TagCollection()
        if len(self) == 0:
            return ret
        _cmpFunc = lambda tag : bool(tag.name == name)
        for tag in self:
            TagCollection._subset(ret, _cmpFunc, tag)

        return ret

    def getElementsByClassName(self, className):
        '''
            getElementsByClassName - Get elements within this collection containing a specific class name

            @param className - A single class name

            @return - TagCollection of unique elements within this collection tagged with a specific class name
        '''
        ret = TagCollection()
        if len(self) == 0:
            return ret
        _cmpFunc = lambda tag : tag.hasClass(className)
        for tag in self:
            TagCollection._subset(ret, _cmpFunc, tag)

        return ret

    def getElementById(self, _id):
        '''
            getElementById - Gets an element within this collection by id

            @param _id - string of "id" attribute

            @return - a single tag matching the id, or None if none found
        '''
        for tag in self:
            if tag.id == _id:
                return tag
            for subtag in tag.children:
                tmp = subtag.getElementById(_id)
                if tmp is not None:
                    return tmp
        return None

    def getElementsByAttr(self, attr, value):
        '''
            getElementsByAttr - Get elements within this collection posessing a given attribute/value pair

            @param attr - Attribute name (lowercase)
            @param value - Matching value

            @return - TagCollection of all elements matching name/value
        '''
        ret = TagCollection()
        if len(self) == 0:
            return ret

        attr = attr.lower()
        _cmpFunc = lambda tag : tag.getAttribute(attr) == value
        for tag in self:
            TagCollection._subset(ret, _cmpFunc, tag)

        return ret

    def getElementsWithAttrValues(self, attr, values):
        '''
            getElementsWithAttrValues - Get elements within this collection possessing an attribute name matching one of several values

            @param attr <lowercase str> - Attribute name (lowerase)
            @param values set<str> - Set of possible matching values

            @return - TagCollection of all elements matching criteria
        '''
        ret = TagCollection()
        if len(self) == 0:
            return ret

        if type(values) != set:
            values = set(values)

        attr = attr.lower()
        _cmpFunc = lambda tag : tag.getAttribute(attr) in values
        for tag in self:
            TagCollection._subset(ret, _cmpFunc, tag)

        return ret

    def getElementsCustomFilter(self, filterFunc):
        '''
            getElementsCustomFilter - Get elements within this collection that match a user-provided function.

            @param filterFunc <function> - A function that returns True if the element matches criteria

            @return - TagCollection of all elements that matched criteria
        '''
        ret = TagCollection()
        if len(self) == 0:
            return ret

        _cmpFunc = lambda tag : filterFunc(tag) is True
        for tag in self:
            TagCollection._subset(ret, _cmpFunc, tag)

        return ret

    def getAllNodes(self):
        '''
            getAllNodes - Gets all the nodes, and all their children for every node within this collection
        '''
        ret = TagCollection()

        for tag in self:
            ret.append(tag)
            ret += tag.getAllChildNodes()

        return ret

    def getAllNodeUids(self):
        '''
            getAllNodeUids - Gets all the internal uids of all nodes, their children, and all their children so on..

              @return set<uuid.UUID>
        '''
        ret = set()

        for child in self:
            ret.update(child.getAllNodeUids())

        return ret

    def contains(self, em):
        '''
            contains - Check if #em occurs within any of the elements within this list, as themselves or as a child, any
               number of levels down.

               To check if JUST an element is contained within this list directly, use the "in" operator.

            @param em <AdvancedTag> - Element of interest

            @return <bool> - True if contained, otherwise False
        '''

        for node in self:
            if node.contains(em):
                return True

        return False

    def containsUid(self, uid):
        '''
            containsUid - Check if #uid is the uid (unique internal identifier) of any of the elements within this list,
              as themselves or as a child, any number of levels down.


            @param uid <uuid.UUID> - uuid of interest

            @return <bool> - True if contained, otherwise False
        '''
        for node in self:
            if node.containsUid(uid):
                return True

        return False


    def filterAll(self, **kwargs):
        '''
            filterAll aka filterAllAnd - Perform a filter operation on ALL nodes in this collection and all their children.

            Results must match ALL the filter criteria. for ANY, use the *Or methods

            For just the nodes in this collection, use "filter" or "filterAnd" on a TagCollection

            For special filter keys, @see #AdvancedHTMLParser.AdvancedHTMLParser.filter

            Requires the QueryableList module to be installed (i.e. AdvancedHTMLParser was installed
              without '--no-deps' flag.)

            For alternative without QueryableList,
              consider #AdvancedHTMLParser.AdvancedHTMLParser.find method or the getElement* methods

            @return TagCollection<AdvancedTag>
        '''
        if canFilterTags is False:
            raise NotImplementedError('filter methods requires QueryableList installed, it is not. Either install QueryableList, or try the less-robust "find" method, or the getElement* methods.')

        allNodes = self.getAllNodes()

        filterableNodes = FilterableTagCollection(allNodes)

        return filterableNodes.filterAnd(**kwargs)

    filterAllAnd = filter

    def filterAllOr(self, **kwargs):
        '''
            filterAllOr - Perform a filter operation on ALL nodes in this collection and all their children.

            Results must match ANY the filter criteria. for ALL, use the *And methods

            For just the nodes in this collection, use "filterOr" on a TagCollection

            For special filter keys, @see #AdvancedHTMLParser.AdvancedHTMLParser.filter

            Requires the QueryableList module to be installed (i.e. AdvancedHTMLParser was installed
              without '--no-deps' flag.)

            For alternative without QueryableList,
              consider #AdvancedHTMLParser.AdvancedHTMLParser.find method or the getElement* methods


            @return TagCollection<AdvancedTag>
        '''
        if canFilterTags is False:
            raise NotImplementedError('filter methods requires QueryableList installed, it is not. Either install QueryableList, or try the less-robust "find" method, or the getElement* methods.')

        allNodes = self.getAllNodes()

        filterableNodes = FilterableTagCollection(allNodes)

        return filterableNodes.filterOr(**kwargs)

    def filter(self, **kwargs):
        '''
            filter aka filterAnd - Perform a filter operation on ALL nodes in this collection (NOT including children, see #filterAnd for that)

            Results must match ALL the filter criteria. for ANY, use the *Or methods

            For special filter keys, @see #AdvancedHTMLParser.AdvancedHTMLParser.filter

            Requires the QueryableList module to be installed (i.e. AdvancedHTMLParser was installed
              without '--no-deps' flag.)

            For alternative without QueryableList,
              consider #AdvancedHTMLParser.AdvancedHTMLParser.find method or the getElement* methods


            @return TagCollection<AdvancedTag>
        '''
        if canFilterTags is False:
            raise NotImplementedError('filter methods requires QueryableList installed, it is not. Either install QueryableList, or try the less-robust "find" method, or the getElement* methods.')

        filterableNodes = FilterableTagCollection(self)

        return filterableNodes.filterAnd(**kwargs)

    filterAnd = filter

    def filterOr(self, **kwargs):
        '''
            filterOr - Perform a filter operation on the nodes in this collection (NOT including children, see #filterAllOr for that)

            Results must match ANY the filter criteria. for ALL, use the *And methods

            For special filter keys, @see #AdvancedHTMLParser.AdvancedHTMLParser.filter

            Requires the QueryableList module to be installed (i.e. AdvancedHTMLParser was installed
              without '--no-deps' flag.)

            For alternative without QueryableList,
              consider #AdvancedHTMLParser.AdvancedHTMLParser.find method or the getElement* methods


            @return TagCollection<AdvancedTag>
        '''
        if canFilterTags is False:
            raise NotImplementedError('filter methods requires QueryableList installed, it is not. Either install QueryableList, or try the less-robust "find" method, or the getElement* methods.')

        filterableNodes = FilterableTagCollection(self)

        return filterableNodes.filterOr(**kwargs)


    def __repr__(self):
        return "%s(%s)" %(self.__class__.__name__, list.__repr__(self))



global canFilterTags

try:
    import QueryableList
    from QueryableList.Base import QueryableListBase

    class FilterableTagCollection(QueryableListBase):

        @staticmethod
        def _get_item_value(item, fieldName):
            fieldName = fieldName.lower()

            if fieldName == 'tagname':
                return item.tagName
            elif fieldName == 'text':
                return item.text
            else:
                return item.getAttribute(fieldName)

        def filterAnd(self, **kwargs):
            ret = QueryableListBase.filterAnd(self, **kwargs)

            return TagCollection(ret)

        filter = filterAnd

        def filterOr(self, **kwargs):
            ret = QueryableListBase.filterOr(self, **kwargs)

            return TagCollection(ret)

    canFilterTags = True

except ImportError:
    class FilterableTagCollection(object):

        def __init__(self, *args, **kwargs):
            raise ImportError('QueryableList is not installed, you cannot use tag filters. Please install QueryableList or use one of the getElement* methods.')

    canFilterTags = False




# Uncomment this line to display the HTML in lists
#    __repr__ = __str__

#vim: set ts=4 sw=4 expandtab
