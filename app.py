from flask import Flask, render_template, request
from health import health_conditions,select_pose,yoga_poses
import pickle
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')
'''
@app.route('/other_page', methods=['GET', 'POST'])
def other_page():
    if request.method == 'POST':
        selected_conditions = request.form.getlist('condition')
        recommended_pose = select_pose(selected_conditions)
        if recommended_pose:
            pose_info = yoga_poses[recommended_pose]
            pose_description = pose_info['description']
            image_url = pose_info['image_url']
            yt_link = pose_info['yt_tutorial_link']
            return render_template('recommendation.html', pose=recommended_pose, description=pose_description, image_url=image_url, yt_link=yt_link)
        else:
            return render_template('error.html')  # A simple template when no poses are left
    return render_template('other_page.html', conditions=health_conditions.keys())
'''
@app.route('/other_page', methods=['GET', 'POST'])
def other_page():
    if request.method == 'POST':
        selected_conditions = request.form.getlist('condition')
        recommended_poses = select_pose(selected_conditions)
        if recommended_poses:
            pose_info_list = []
            
            for recommended_pose in recommended_poses:
                pose_info = yoga_poses[recommended_pose]
                pose_description = pose_info['description']
                image_url = pose_info['image_url']
                yt_link = pose_info['yt_tutorial_link']
                pose_info_list.append({'pose': recommended_pose, 'description': pose_description, 'image_url': image_url, 'yt_link': yt_link})
            return render_template('recommendation.html',selected_conditions=selected_conditions, poses_info=pose_info_list)
        else:
            return render_template('error.html')  # A simple template when no poses are left
    return render_template('other_page.html', conditions=health_conditions.keys())

if __name__ == '__main__':
    app.run(debug=True)
