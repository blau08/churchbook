class StudentsController < ApplicationController

  before_action :authenticate_user!, only: [:new, :create]

  def index
    @students = Student.all.order(:firstname)
  end

  def show
    @student = Student.find(params[:id])
  end

  def new
    @student = Student.new
  end

  def create
    @student = Student.new(student_params)
    if @student.save
      redirect_to students_path
    else
      render :new
    end
  end

  def edit
    @student = Student.find(params[:id])
  end

  def update
    @student = Student.find(params[:id])
    if @student.update(student_params)
      redirect_to students_path
    else
      render :edit
    end
  end

  def destroy
    @student = Student.find(params[:id])
    @student.destroy
    redirect_to students_path
  end



private
  def student_params
    params.require(:student).permit(:lastname, :firstname, :chinesename, :dob, :gender, :countryorigin, :parentsorigin, :email, :mobile, :occupation, :fellowship, :congregation, :image )
  end
end
