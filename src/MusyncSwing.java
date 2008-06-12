/**
 * Main class which starts the GUI.
 *
 * Copyright: John-John Tedro, Oscar Eriksson (2008)
 *
 *   This file is part of musync-swing.
 *
 *   musync-swing is free software: you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation, either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   musync-swing is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *   GNU General Public License for more details.
 *
 *   You should have received a copy of the GNU General Public License
 *   along with musync-swing.  If not, see <http://www.gnu.org/licenses/>.
 */
public class MusyncSwing implements Runnable
{
    public static void main(String[] args)
    {
        // Schedule a job for the event-dispatching thread:
        // creating and showing this application's GUI.
        javax.swing.SwingUtilities.invokeLater(new MusyncSwing());
    }

    public void run() {
        try {
            MainFrame frame = new MainFrame();
            frame.pack();
            Commons.center(frame, 1000, 600);
            frame.setSize(1000,600);
            frame.setVisible(true);
           
            Commons.setup();

            // Check if we have musync.
            if (!Commons.checkForMusyncInPath()) {
                Commons.epopup("musync could not be found in your PATH, this program will not work properly");
            } else {
                // Try to read configuration from musync.
                String[] cmd = {"musync","--export"};
                ExportMusync export = new ExportMusync(cmd, frame);
                export.start();
            }
        }
        catch(Exception e) {
            Commons.eprint("Exception caught:\n    %s", e);
            e.printStackTrace(System.err);
        }
    }
}
