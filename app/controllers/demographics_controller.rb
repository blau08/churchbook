class DemographicsController < ApplicationController
  helper_method :sort_column, :sort_direction

  def index
    @students = Student.all.order(sort_column + " " + sort_direction)
    @students_bar = Student.all
  end

  def age
    now = Time.now.utc.to_date
    now.year - self.year - (self.change(:year => now.year) > now ? 1 : 0)
  end


private

  def sort_column
    Student.column_names.include?(params[:sort]) ? params[:sort] : "lastname"
  end

  def sort_direction
    %w[asc desc].include?(params[:direction]) ? params[:direction] : "asc"
  end
end
