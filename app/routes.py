from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, current_user, login_required
try:
    from werkzeug.urls import url_parse  # Werkzeug < 2.3
except ImportError:
    from urllib.parse import urlparse as url_parse  # Fallback
from app import db
from app.models import User, Skill, SwapRequest
from app.forms import LoginForm, RegistrationForm, SkillForm, SwapRequestForm, ProfileSettingsForm

# ======================
# Blueprint Initialization
# ======================

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')
profile_bp = Blueprint('profile', __name__, url_prefix='/profile')
swaps_bp = Blueprint('swaps', __name__, url_prefix='/swaps')
main_bp = Blueprint('main', __name__)

# ======================
# Authentication Routes
# ======================

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.login'))
        
        login_user(user, remember=form.remember.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    form = RegistrationForm()
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data.strip().lower()).first()
        if existing_user:
            flash('Email already registered. Please use a different email.', 'danger')
            return redirect(url_for('auth.register'))
            
        existing_username = User.query.filter_by(username=form.username.data.strip()).first()
        if existing_username:
            flash('Username already taken. Please choose a different username.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create new user
        user = User(
            username=form.username.data.strip(),
            email=form.email.data.strip().lower()
        )
        user.set_password(form.password.data)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Automatically log in the new user
            login_user(user)
            
            flash(f'Welcome to SkillSwap, {user.username}! Your account has been created successfully.', 'success')
            return redirect(url_for('main.dashboard'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
    
    return render_template('auth/register.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out successfully.', 'info')
    return redirect(url_for('main.home'))

@auth_bp.route('/oauth/<provider>')
def oauth_login(provider):
    """OAuth login route - placeholder for future implementation"""
    flash(f'{provider.title()} login coming soon!', 'info')
    return redirect(url_for('auth.login'))

@auth_bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # Basic form handling - you'll need to create ResetPasswordRequestForm
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        if email:
            user = User.query.filter_by(email=email).first()
            if user:
                # TODO: Implement email sending logic
                flash('Check your email for password reset instructions.', 'info')
            else:
                flash('Email address not found.', 'danger')
        else:
            flash('Please enter an email address.', 'danger')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/reset_password_request.html')

@auth_bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    # TODO: Implement token verification and password reset
    flash('Password reset functionality coming soon!', 'info')
    return redirect(url_for('auth.login'))

# ======================
# Profile Routes
# ======================

@profile_bp.route('')
@login_required
def view():
    offered_skills = Skill.query.filter_by(offered_by_id=current_user.id).all()
    wanted_skills = Skill.query.filter_by(wanted_by_id=current_user.id).all()
    return render_template('profile/view.html', 
                         user=current_user,
                         offered_skills=offered_skills,
                         wanted_skills=wanted_skills)

@profile_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    form = ProfileSettingsForm(obj=current_user)
    if form.validate_on_submit():
        # Check if username is being changed and if it's available
        if form.username.data.strip() != current_user.username:
            existing_user = User.query.filter_by(username=form.username.data.strip()).first()
            if existing_user:
                flash('Username already taken. Please choose a different username.', 'danger')
                return redirect(url_for('profile.edit'))
        
        try:
            current_user.username = form.username.data.strip()
            current_user.location = form.location.data.strip() if form.location.data else None
            current_user.is_public = form.is_public.data
            db.session.commit()
            flash('Your profile has been updated!', 'success')
            return redirect(url_for('profile.view'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while updating your profile. Please try again.', 'danger')
            return redirect(url_for('profile.edit'))
    
    return render_template('profile/edit.html', form=form)

@profile_bp.route('/skill/add', methods=['GET', 'POST'])
@login_required
def add_skill():
    form = SkillForm()
    if form.validate_on_submit():
        try:
            skill = Skill(
                name=form.name.data.strip(),
                offered_by_id=current_user.id if form.skill_type.data == 'offered' else None,
                wanted_by_id=current_user.id if form.skill_type.data == 'wanted' else None,
                availability=form.availability.data.strip() if form.availability.data else None
            )
            db.session.add(skill)
            db.session.commit()
            
            skill_type = "offered" if form.skill_type.data == 'offered' else "wanted"
            flash(f'Skill "{skill.name}" added to your {skill_type} skills!', 'success')
            return redirect(url_for('profile.view'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the skill. Please try again.', 'danger')
            return redirect(url_for('profile.add_skill'))
    
    return render_template('profile/add_skill.html', form=form)

@profile_bp.route('/skill/<int:skill_id>/delete', methods=['POST'])
@login_required
def delete_skill(skill_id):
    skill = Skill.query.get_or_404(skill_id)
    
    # Check if user owns this skill
    if skill.offered_by_id != current_user.id and skill.wanted_by_id != current_user.id:
        abort(403)
    
    try:
        skill_name = skill.name
        db.session.delete(skill)
        db.session.commit()
        flash(f'Skill "{skill_name}" has been deleted.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while deleting the skill. Please try again.', 'danger')
    
    return redirect(url_for('profile.view'))

# ======================
# Swap Routes
# ======================

@swaps_bp.route('/browse')
@login_required
def browse():
    search_query = request.args.get('q', '').strip()
    skill_filter = request.args.get('skill', '').strip()
    
    # Base query - exclude current user and only show public profiles
    query = User.query.filter(
        User.is_public == True,
        User.id != current_user.id
    )
    
    if search_query:
        query = query.filter(User.username.ilike(f'%{search_query}%'))
    
    if skill_filter:
        query = query.filter(
            (User.skills_offered.any(Skill.name.ilike(f'%{skill_filter}%'))) |
            (User.skills_wanted.any(Skill.name.ilike(f'%{skill_filter}%')))
        )
    
    users = query.all()
    return render_template('swaps/browse.html', 
                         users=users, 
                         search_query=search_query,
                         skill_filter=skill_filter)

@swaps_bp.route('/request/<int:user_id>', methods=['GET', 'POST'])
@login_required
def send_request(user_id):
    receiver = User.query.get_or_404(user_id)
    
    # Check if user is trying to send request to themselves
    if receiver.id == current_user.id:
        flash('You cannot send a swap request to yourself.', 'warning')
        return redirect(url_for('swaps.browse'))
    
    # Check if request already exists
    existing_request = SwapRequest.query.filter_by(
        sender_id=current_user.id,
        receiver_id=receiver.id,
        status='pending'
    ).first()
    
    if existing_request:
        flash('You already have a pending request with this user.', 'warning')
        return redirect(url_for('swaps.browse'))
    
    form = SwapRequestForm()
    if form.validate_on_submit():
        try:
            swap = SwapRequest(
                sender_id=current_user.id,
                receiver_id=receiver.id,
                message=form.message.data.strip() if form.message.data else None
            )
            db.session.add(swap)
            db.session.commit()
            flash(f'Swap request sent to {receiver.username} successfully!', 'success')
            return redirect(url_for('swaps.browse'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while sending the request. Please try again.', 'danger')
            return redirect(url_for('swaps.send_request', user_id=user_id))
    
    return render_template('swaps/send_request.html', form=form, receiver=receiver)

@swaps_bp.route('/requests')
@login_required
def manage_requests():
    received = SwapRequest.query.filter_by(receiver_id=current_user.id).order_by(SwapRequest.created_at.desc()).all()
    sent = SwapRequest.query.filter_by(sender_id=current_user.id).order_by(SwapRequest.created_at.desc()).all()
    return render_template('swaps/requests.html', received=received, sent=sent)

@swaps_bp.route('/request/<int:request_id>/accept', methods=['POST'])
@login_required
def accept_request(request_id):
    swap = SwapRequest.query.get_or_404(request_id)
    
    # Check if user is the receiver and request is pending
    if swap.receiver_id != current_user.id:
        abort(403)
    
    if swap.status != 'pending':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('swaps.manage_requests'))
    
    try:
        swap.status = 'accepted'
        db.session.commit()
        flash(f'Swap request from {swap.sender.username} accepted!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while accepting the request. Please try again.', 'danger')
    
    return redirect(url_for('swaps.manage_requests'))

@swaps_bp.route('/request/<int:request_id>/reject', methods=['POST'])
@login_required
def reject_request(request_id):
    swap = SwapRequest.query.get_or_404(request_id)
    
    # Check if user is the receiver and request is pending
    if swap.receiver_id != current_user.id:
        abort(403)
    
    if swap.status != 'pending':
        flash('This request has already been processed.', 'warning')
        return redirect(url_for('swaps.manage_requests'))
    
    try:
        swap.status = 'rejected'
        db.session.commit()
        flash(f'Swap request from {swap.sender.username} rejected.', 'info')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while rejecting the request. Please try again.', 'danger')
    
    return redirect(url_for('swaps.manage_requests'))

@swaps_bp.route('/request/<int:request_id>/complete', methods=['POST'])
@login_required
def complete_request(request_id):
    swap = SwapRequest.query.get_or_404(request_id)
    
    # Check if user is involved in this swap and it's accepted
    if swap.sender_id != current_user.id and swap.receiver_id != current_user.id:
        abort(403)
    
    if swap.status != 'accepted':
        flash('This request cannot be completed in its current state.', 'warning')
        return redirect(url_for('swaps.manage_requests'))
    
    try:
        swap.status = 'completed'
        db.session.commit()
        flash('Swap marked as completed!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('An error occurred while completing the swap. Please try again.', 'danger')
    
    return redirect(url_for('swaps.manage_requests'))

# ======================
# Main Routes
# ======================

@main_bp.route('/')
def index():
    """Root route - no redirects"""
    if current_user.is_authenticated:
        # Get user's skills for the dashboard
        try:
            offered_skills = Skill.query.filter_by(offered_by_id=current_user.id).all()
            wanted_skills = Skill.query.filter_by(wanted_by_id=current_user.id).all()
            
            # Get recent swap requests
            recent_requests = SwapRequest.query.filter(
                (SwapRequest.sender_id == current_user.id) | 
                (SwapRequest.receiver_id == current_user.id)
            ).order_by(SwapRequest.created_at.desc()).limit(5).all()
            
            return render_template('main/dashboard.html', 
                                 offered_skills=offered_skills, 
                                 wanted_skills=wanted_skills,
                                 recent_requests=recent_requests)
        except Exception as e:
            # If dashboard fails, show a simple authenticated page
            return render_template('main/dashboard.html')
    else:
        # Show landing page for non-authenticated users
        return render_template('main/landing.html')

@main_bp.route('/home')
def home():
    """Home page - redirect to index to avoid loops"""
    return redirect(url_for('main.index'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard - redirect to index to avoid loops"""
    return redirect(url_for('main.index'))

# ======================
# Error Handlers
# ======================

@main_bp.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@main_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

@main_bp.errorhandler(403)
def forbidden_error(error):
    return render_template('errors/403.html'), 403

# ======================
# Additional Utility Routes
# ======================

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('main/about.html')

@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('main/contact.html')

@main_bp.route('/search')
@login_required
def search():
    """Global search functionality"""
    query = request.args.get('q', '').strip()
    if not query:
        return redirect(url_for('main.dashboard'))
    
    # Search users
    users = User.query.filter(
        User.is_public == True,
        User.id != current_user.id,
        User.username.ilike(f'%{query}%')
    ).limit(10).all()
    
    # Search skills
    skills = Skill.query.filter(
        Skill.name.ilike(f'%{query}%')
    ).limit(10).all()
    
    return render_template('main/search_results.html', 
                         query=query, 
                         users=users, 
                         skills=skills)
