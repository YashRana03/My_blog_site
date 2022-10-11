@app.route('/login', methods=['POST', 'GET'])
def login():
    form = UserLoginForm()
    if form.validate_on_submit():
        hashed_salted_password = User.query.filter_by(email=form.email.data).first
        if check_password_hash(hashed_salted_password, form.password.data):
            return redirect(url_for('get_all_posts'))
    return render_template("login.html", form=form)


