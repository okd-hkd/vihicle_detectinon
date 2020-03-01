# coding: utf-8

from flask import Flask, jsonify, render_template, request, redirect, url_for, send_from_directory, session
from werkzeug import secure_filename

from skimage.io import imread
from skimage.filters import threshold_otsu
import matplotlib.pyplot as plt


import os, io, time, re

MODEL_FILE_PATH = 'model_corona_002auto.ftz'

#　flask appを使えるようにするためのインスんタンス化
app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False  # 日本語文字ばけ防止

@app.route('/', methods=["GET", "POST"])
def post_json():
    if  request.method == "GET":
        return render_template('test_ajax.html')
    
    elif request.method == "POST":
        
        filename = app.request.files.get('imagefile', '')
            
        # filename = './video12.mp4'
        
        import cv2
        cap = cv2.VideoCapture(filename)
        # cap = cv2.VideoCapture(0)
        count = 0
        
        while cap.isOpened():
            ret,frame = cap.read()
            if ret == True:
                # cv2.imshow('window-name',frame)
                cv2.imwrite("./output/frame%d.jpg" % count, frame)
                count = count + 1
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break
            else:
                break
        cap.release()
        cv2.destroyAllWindows()
        
        # car image -> grayscale image -> binary image
        import imutils
        car_image = imread("./output/frame%d.jpg"%(count-1), as_gray=True)
        car_image = imutils.rotate(car_image, 270)
        # car_image = imread("car.png", as_gray=True)
        # it should be a 2 dimensional array
        print(car_image.shape)
        
        # the next line is not compulsory however, a grey scale pixel
        # in skimage ranges between 0 & 1. multiplying it with 255
        # will make it range between 0 & 255 (something we can relate better with
        
        gray_car_image = car_image * 255
        fig, (ax1, ax2) = plt.subplots(1, 2)
        ax1.imshow(gray_car_image, cmap="gray")
        threshold_value = threshold_otsu(gray_car_image)
        binary_car_image = gray_car_image > threshold_value
        # print(binary_car_image)
        ax2.imshow(binary_car_image, cmap="gray")
        # ax2.imshow(gray_car_image, cmap="gray")
        plt.show()
        
        # CCA (finding connected regions) of binary image
        
        
        from skimage import measure
        from skimage.measure import regionprops
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
        
        # this gets all the connected regions and groups them together
        label_image = measure.label(binary_car_image)
        
        # print(label_image.shape[0]) #width of car img
        
        # getting the maximum width, height and minimum width and height that a license plate can be
        plate_dimensions = (0.03*label_image.shape[0], 0.08*label_image.shape[0], 0.15*label_image.shape[1], 0.3*label_image.shape[1])
        plate_dimensions2 = (0.08*label_image.shape[0], 0.2*label_image.shape[0], 0.15*label_image.shape[1], 0.4*label_image.shape[1])
        min_height, max_height, min_width, max_width = plate_dimensions
        plate_objects_cordinates = []
        plate_like_objects = []
        
        fig, (ax1) = plt.subplots(1)
        ax1.imshow(gray_car_image, cmap="gray")
        flag =0
        # regionprops creates a list of properties of all the labelled regions
        for region in regionprops(label_image):
            # print(region)
            if region.area < 50:
                #if the region is so small then it's likely not a license plate
                continue
                # the bounding box coordinates
            min_row, min_col, max_row, max_col = region.bbox
            # print(min_row)
            # print(min_col)
            # print(max_row)
            # print(max_col)
        
            region_height = max_row - min_row
            region_width = max_col - min_col
            # print(region_height)
            # print(region_width)
        
            # ensuring that the region identified satisfies the condition of a typical license plate
            if region_height >= min_height and region_height <= max_height and region_width >= min_width and region_width <= max_width and region_width > region_height:
                flag = 1
                plate_like_objects.append(binary_car_image[min_row:max_row,
                                          min_col:max_col])
                plate_objects_cordinates.append((min_row, min_col,
                                                 max_row, max_col))
                rectBorder = patches.Rectangle((min_col, min_row), max_col - min_col, max_row - min_row, edgecolor="red",
                                               linewidth=2, fill=False)
                ax1.add_patch(rectBorder)
                # let's draw a red rectangle over those regions
        if(flag == 1):
            # print(plate_like_objects[0])
            plt.show()
        
        
        
        
        if(flag==0):
            min_height, max_height, min_width, max_width = plate_dimensions2
            plate_objects_cordinates = []
            plate_like_objects = []
        
            fig, (ax1) = plt.subplots(1)
            ax1.imshow(gray_car_image, cmap="gray")
        
            # regionprops creates a list of properties of all the labelled regions
            for region in regionprops(label_image):
                if region.area < 50:
                    #if the region is so small then it's likely not a license plate
                    continue
                    # the bounding box coordinates
                min_row, min_col, max_row, max_col = region.bbox
                # print(min_row)
                # print(min_col)
                # print(max_row)
                # print(max_col)
        
                region_height = max_row - min_row
                region_width = max_col - min_col
                # print(region_height)
                # print(region_width)
        
                # ensuring that the region identified satisfies the condition of a typical license plate
                if region_height >= min_height and region_height <= max_height and region_width >= min_width and region_width <= max_width and region_width > region_height:
                    # print("hello")
                    plate_like_objects.append(binary_car_image[min_row:max_row,
                                              min_col:max_col])
                    plate_objects_cordinates.append((min_row, min_col,
                                                     max_row, max_col))
                    rectBorder = patches.Rectangle((min_col, min_row), max_col - min_col, max_row - min_row, edgecolor="red",
                                                   linewidth=2, fill=False)
                    ax1.add_patch(rectBorder)
                    # let's draw a red rectangle over those regions
            # print(plate_like_objects[0])
            plt.show()
            
            import SegmentCharacters
            import pickle
            print("Loading model")
            filename = './finalized_model.sav'
            
            model = pickle.load(open(filename, 'rb'))
            
            print('Model loaded. Predicting characters of number plate')
            classification_result = []
            for each_character in SegmentCharacters.characters:
                # converts it to a 1D array
                each_character = each_character.reshape(1, -1);
                result = model.predict(each_character)
                classification_result.append(result)
            
            print('Classification result')
            print(classification_result)
            
            plate_string = ''
            for eachPredict in classification_result:
                plate_string += eachPredict[0]
            
            print('Predicted license plate')
            print(plate_string)
            
            # it's possible the characters are wrongly arranged
            # since that's a possibility, the column_list will be
            # used to sort the letters in the right order
            
            column_list_copy = SegmentCharacters.column_list[:]
            SegmentCharacters.column_list.sort()
            rightplate_string = ''
            for each in SegmentCharacters.column_list:
                rightplate_string += plate_string[column_list_copy.index(each)]
            
            print('License plate')
            print(rightplate_string)
                    
                
                
            json = [
                  {"License plate": rightplate_string},
                #   {"Confidence": probability}
                  ]
            return jsonify(json)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))