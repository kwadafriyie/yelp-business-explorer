import json
import sys


def cleanStr4SQL(str):
    return str.replace("'","''").replace("\n"," ").replace("\r"," ")

def quote(value):
    return "'" + cleanStr4SQL(str(value)) + "'"

def getAttributes(attributes):
    L = []
    for (attribute, value) in list(attributes.items()):
        if isinstance(value, dict):
            L += getAttributes(value)
        else:
            L.append((attribute, value))
    return L

def parseBusinessData(max_lines=None, suffix=''):
    print ("Parsing Businesses...")
    with open('.//yelp_business.JSON', 'r') as source: #read JSON file
        business_out = open('.//business_insert' + suffix + '.sql', 'w')
        category_out = open('.//category_insert' + suffix + '.sql', 'w')
        bus_cat_out = open('.//business_category_insert' + suffix + '.sql', 'w')
        bus_attr_out = open('.//business_attribute_insert' + suffix + '.sql', 'w')

        category_ids = {} #category name -> category_id, assigned in first-seen order
        line = source.readline()
        line_count = 0

        while line:# read each JSON abject and get data
            data = json.loads(line)
            business = data['business_id'] #business id
            # num_checkins and reviewrating are loaded as 0 / 0.0 and overwritten by a later UPDATE step
            business_out.write("INSERT INTO Business (business_id, name, address, city, state, zipcode, stars, review_count, is_open, num_checkins, reviewrating) VALUES (" + \
                        quote(business) + "," + \
                        quote(data['name']) + "," + \
                        quote(data['address']) + "," + \
                        quote(data['city']) + "," + \
                        quote(data['state']) + "," + \
                        quote(data['postal_code']) + "," + \
                        str(data['stars']) + "," + \
                        str(data['review_count']) + "," + \
                        str(data['is_open']) + "," + \
                        "0,0.0);\n")

        #proceses business fields
            #categories
            seen_categories = set()
            for category in data['categories']:
                if category not in category_ids:
                    category_ids[category] = len(category_ids) + 1
                if category not in seen_categories: #PK is (business_id, category_id)
                    seen_categories.add(category)
                    bus_cat_out.write("INSERT INTO Business_Category (business_id, category_id) VALUES (" + \
                                quote(business) + "," + str(category_ids[category]) + ");\n")

            #attributes
            seen_attributes = set()
            for (attr,value) in getAttributes(data['attributes']):
                if attr not in seen_attributes: #PK is (business_id, attribute_name)
                    seen_attributes.add(attr)
                    bus_attr_out.write("INSERT INTO Business_Attribute (business_id, attribute_name, attribute_value) VALUES (" + \
                                quote(business) + "," + quote(attr) + "," + quote(value) + ");\n")

            line = source.readline()
            line_count +=1
            if max_lines and line_count >= max_lines:
                break
        print(line_count)

        #deduplicated categories, one INSERT per unique name with an explicit id
        for (name, category_id) in sorted(category_ids.items(), key=lambda item: item[1]):
            category_out.write("INSERT INTO Category (category_id, name) VALUES (" + \
                        str(category_id) + "," + quote(name) + ");\n")
        if category_ids:
            #keep the SERIAL sequence in sync with the explicit ids
            category_out.write("SELECT setval(pg_get_serial_sequence('category', 'category_id'), " + str(len(category_ids)) + ");\n")

        business_out.close()
        category_out.close()
        bus_cat_out.close()
        bus_attr_out.close()


def parseUserData(max_lines=None, suffix=''):
    print ("Parsing Users...")
    with open('.//yelp_user.JSON', 'r') as source: #read JSON file
        outfile =  open('.//yelp_user_insert' + suffix + '.sql', 'w')
        line = source.readline()
        line_count = 0

        while line: # read each JSON abject and get data
            data = json.loads(line)
            outfile.write("INSERT INTO Yelp_User (user_id, name, yelping_since, review_count, fans, avg_stars, funny, useful, cool) VALUES (" + \
                    quote(data['user_id']) + "," + \
                    quote(data["name"]) + "," + \
                    quote(data["yelping_since"]) + "," + \
                    str(data['review_count']) + "," + \
                    str(data['fans']) + "," + \
                    str(data['average_stars']) + "," + \
                    str(data['funny']) + "," + \
                    str(data['useful']) + "," + \
                    str(data['cool']) + ");\n")

            line = source.readline()
            line_count +=1
            if max_lines and line_count >= max_lines:
                break

        print(line_count)
        outfile.close()


def parseReviewData(max_lines=None, suffix=''):
    print ("Parsing Reviews...")
    with open('.//yelp_review.JSON', 'r') as source: #read JSON file
        outfile =  open('.//review_insert' + suffix + '.sql', 'w')
        line = source.readline()
        line_count = 0

        while line: # read each JSON abject and get data
            data = json.loads(line)
            outfile.write("INSERT INTO Review (review_id, business_id, user_id, stars, date, text, useful, funny, cool) VALUES (" + \
                    quote(data["review_id"]) + "," + \
                    quote(data["business_id"]) + "," + \
                    quote(data["user_id"]) + "," + \
                    str(data['stars']) + "," + \
                    quote(data["date"]) + "," + \
                    quote(data["text"]) + "," + \
                    str(data['useful']) + "," + \
                    str(data['funny']) + "," + \
                    str(data['cool']) + ");\n")

            line = source.readline()
            line_count +=1
            if max_lines and line_count >= max_lines:
                break

        print(line_count)
        outfile.close()


def parseCheckinData(max_lines=None, suffix=''):
    print ("Parsing Checkins...")
    with open('.//yelp_checkin.JSON', 'r') as source: #read JSON file
        outfile =  open('.//checkin_insert' + suffix + '.sql', 'w')
        line = source.readline()
        line_count = 0

        while line: # read each JSON abject and get data
            data = json.loads(line)
            business_id = data['business_id']
            for (dayofweek,time) in data['time'].items():
                for (hour,count) in time.items():
                    outfile.write("INSERT INTO Checkin (business_id, day, time, count) VALUES (" + \
                                quote(business_id) + "," + \
                                quote(dayofweek) + "," + \
                                quote(hour) + "," + \
                                str(count) + ");\n")

            line = source.readline()
            line_count +=1
            if max_lines and line_count >= max_lines:
                break

        print(line_count)
        outfile.close()


if __name__ == '__main__':
    # optional arg: number of JSON lines per file, for sample runs (writes *_sample.sql)
    max_lines = None
    suffix = ''
    if len(sys.argv) > 1:
        max_lines = int(sys.argv[1])
        suffix = '_sample'

    parseBusinessData(max_lines, suffix)
    parseUserData(max_lines, suffix)
    parseReviewData(max_lines, suffix)
    parseCheckinData(max_lines, suffix)
