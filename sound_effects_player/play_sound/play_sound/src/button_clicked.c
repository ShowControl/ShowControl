/*
 * button_clicked.c
 *
 * Copyright © 2015 by John Sauter <John_Sauter@systemeyescomputerstore.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <http://www.gnu.org/licenses/>.
 */
#include "button_clicked.h"
#include "play_sound.h"

/* The Start button has been pushed.  Turn the sound on. */
void
start_clicked (GtkButton * button, gpointer user_data)
{
  GstElement *pipeline;

  pipeline = play_sound_get_pipeline (user_data);
  gst_element_set_state (pipeline, GST_STATE_PLAYING);

  /* Change the text on the button from "Start" to "Playing". */
  gtk_button_set_label (button, "Playing");
  return;
}

/* The stop button has been pushed.  Turn the sound off. */
void
stop_clicked (GtkButton * button, gpointer user_data)
{
  GstElement *pipeline;
  GtkButton *start_button = NULL;
  GtkWidget *parent_container;
  GList *children_list = NULL;
  const gchar *child_name = NULL;

  pipeline = play_sound_get_pipeline (user_data);
  gst_element_set_state (pipeline, GST_STATE_PAUSED);

  /* Find the start button and set its text back to "Start". */
  parent_container = gtk_widget_get_parent (GTK_WIDGET (button));
  children_list =
    gtk_container_get_children (GTK_CONTAINER (parent_container));
  while (children_list != NULL)
    {
      child_name = gtk_widget_get_name (children_list->data);
      if (g_ascii_strcasecmp (child_name, "start_button") == 0)
	{
	  start_button = children_list->data;
	  break;
	}
      children_list = children_list->next;
    }
  g_list_free (children_list);

  if (start_button != NULL)
    {
      gtk_button_set_label (start_button, "Start");
    }

  return;
}

/* The volume slider has been moved.  Update the volume and the display. */
void
play_sound_volume_changed (GtkButton * button, gpointer user_data)
{
  GtkLabel *volume_label = NULL;
  GtkWidget *parent_container;
  GList *children_list = NULL;
  const gchar *child_name = NULL;
  GstElement *pipeline_element, *volume_element;
  gdouble new_value;
  gchar *value_string;

  /* Adjust the volume. */
  pipeline_element = play_sound_get_pipeline (user_data);
  volume_element = gst_bin_get_by_name (GST_BIN (pipeline_element), "volume");
  if (volume_element == NULL)
    return;
  new_value = gtk_scale_button_get_value (GTK_SCALE_BUTTON (button));
  g_object_set (volume_element, "volume", new_value, NULL);

  /* Update the display. */
  parent_container = gtk_widget_get_parent (GTK_WIDGET (button));
  /* Find the volume label */
  children_list =
    gtk_container_get_children (GTK_CONTAINER (parent_container));
  while (children_list != NULL)
    {
      child_name = gtk_widget_get_name (children_list->data);
      if (g_ascii_strcasecmp (child_name, "volume_label") == 0)
	{
	  volume_label = children_list->data;
	  break;
	}
      children_list = children_list->next;
    }
  g_list_free (children_list);

  if (volume_label != NULL)
    {
      /* Update the text in the volume label. */
      value_string = g_strdup_printf ("Vol %3.0f%%", new_value * 100.0);
      gtk_label_set_text (volume_label, value_string);
      g_free (value_string);
    }

  return;
}

/* The pan slider has been moved.  Update the pan and display. */
void
play_sound_pan_changed (GtkButton * button, gpointer user_data)
{
  GstElement *pipeline_element, *pan_element;
  gdouble new_value;
  GtkLabel *pan_label = NULL;
  GtkWidget *parent_container;
  GList *children_list = NULL;
  const gchar *child_name = NULL;
  gchar *value_string;

  /* Adjust the pan. */
  pipeline_element = play_sound_get_pipeline (user_data);
  pan_element = gst_bin_get_by_name (GST_BIN (pipeline_element), "pan");
  if (pan_element == NULL)
    return;
  new_value = gtk_scale_button_get_value (GTK_SCALE_BUTTON (button));
  new_value = (new_value - 50.0) / 50.0;
  g_object_set (pan_element, "panorama", new_value, NULL);

  /* Update the display. */
  parent_container = gtk_widget_get_parent (GTK_WIDGET (button));
  /* Find the pan label. */
  children_list =
    gtk_container_get_children (GTK_CONTAINER (parent_container));
  while (children_list != NULL)
    {
      child_name = gtk_widget_get_name (children_list->data);
      if (g_ascii_strcasecmp (child_name, "pan_label") == 0)
	{
	  pan_label = children_list->data;
	  break;
	}
      children_list = children_list->next;
    }
  g_list_free (children_list);

  if (pan_label != NULL)
    {
      /* Update the text of the label.  0.0 corresponds to Center, 
       * negative numbers to left, and positive numbers to right. */
      if (new_value == 0.0)
	gtk_label_set_text (pan_label, "Center");
      else
	{
	  if (new_value < 0.0)
	    value_string =
	      g_strdup_printf ("Left %3.0f%%", -(new_value * 100.0));
	  else
	    value_string =
	      g_strdup_printf ("Right %3.0f%%", new_value * 100.0);
	  gtk_label_set_text (pan_label, value_string);
	  g_free (value_string);
	}
    }
  return;
}
