from flask import Blueprint, render_template, request, session, redirect, url_for

payment_bp = Blueprint('payment_bp', __name__,
                       template_folder='../../templates')


@payment_bp.route('/', methods=['GET', 'POST'])
def pay():
    if request.method == 'POST':
        method = request.form['method']
        session['payment_mode'] = method
        if method == 'qr':
            return render_template('payment.html', show_qr=True)
        return redirect(url_for('payment_bp.success'))

    return render_template('payment.html')


@payment_bp.route('/success')
def success():
    method = session.get('payment_mode', 'unknown')
    return render_template('payment_success.html', method=method)
