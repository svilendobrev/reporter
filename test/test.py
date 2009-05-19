import row
import packet
import group
import row_classifier as rc
import viewer
from test_set import *
import link

cases = []
cases.append( get_test_suite( row.all_cases     , row.RowCase       ))
cases.append( get_test_suite( group.all_cases   , group.GrpCase     ))
cases.append( get_test_suite( rc.all_cases      , rc.ClassifierCase ))
#cases.append( get_test_suite( viewer.all_cases  , viewer.ViewCase   ))
cases.append( get_test_suite( link.all_cases      , link.RegularTestCase))

s = unittest.TestSuite( cases)

if __name__ == "__main__":
    unittest.TextTestRunner(unittest.sys.stdout, verbosity=3, descriptions=True, ).run( s)

