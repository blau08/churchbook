class CreateSchedules < ActiveRecord::Migration
  def change
    create_table :schedules do |t|
      t.string :title
      t.string :description
      t.date :date
      t.time :time
      t.string :maker

      t.timestamps null: false
    end
  end
end
