# Copyright (c) 2015 Tim Savannah under LGPLv3. 
# See LICENSE (https://gnu.org/licenses/lgpl-3.0.txt) for more information.
#  Exceptions used

class MultipleRootNodeException(Exception):
    '''
        Exception raised and used internally when you try to use multiple root nodes
          Example:
            <one>
              <b>Hi</b>
              <i>Hello</i>
            </one>
            <two>
              <b>Cheese</b>
              <i>Ssdf</i>
            </two>

        This is legal, a fake root node "xxxblank" will be set at head, and all methods will ignore it.
    '''
    pass

#vim: set ts=4 sw=4 expandtab
